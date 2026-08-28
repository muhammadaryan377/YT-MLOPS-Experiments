from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.schemas import Product


BALANCE_TERMS = {
    "balance", "hisaab", "hisab", "due", "outstanding", "pichla", "previous balance"
}
FILLER = {
    "bhej", "bhejna", "bhejdena", "bhej dena", "send", "please", "pls", "chahiye", "chaheye",
    "aur", "and", "bhi", "kal", "aaj", "kar", "dena", "de", "do"
}


@dataclass
class ParsedItem:
    product: Product
    quantity: int
    unit: str
    segment: str


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower().strip()
    text = text.replace("×", "x")
    text = re.sub(r"(?<=\d)\s*\.\s*(?=\d)", ".", text)
    text = re.sub(r"\s+", " ", text)
    return text


def wants_balance(text: str) -> bool:
    normalized = normalize_text(text)
    return any(term in normalized for term in BALANCE_TERMS)


def _split_segments(text: str) -> list[str]:
    parts = re.split(r"[,;\n]+|\s+(?:aur|and|plus)\s+", normalize_text(text))
    return [p.strip(" .!?") for p in parts if p.strip(" .!?")]


def _best_product(segment: str, products: list[Product]) -> tuple[Product | None, float]:
    best_product = None
    best_score = 0.0
    for product in products:
        for alias in product.aliases:
            if alias in segment:
                score = min(1.0, 0.92 + (len(alias) / max(len(segment), 1)) * 0.08)
            else:
                score = SequenceMatcher(None, alias, segment).ratio()
            if score > best_score:
                best_score = score
                best_product = product
    return best_product, best_score


def _extract_quantity(segment: str, product: Product) -> tuple[int | None, str]:
    alias_positions: list[int] = []
    for alias in product.aliases:
        pos = segment.find(alias)
        if pos >= 0:
            alias_positions.append(pos)
    product_pos = min(alias_positions) if alias_positions else len(segment)

    prefix = segment[:product_pos]
    pattern = r"\b(\d{1,4})\b(?:\s*(cartons?|ctns?|ctn|peti(?:an)?|cases?|pcs|pieces?))?"
    matches = list(re.finditer(pattern, prefix))
    if not matches:
        matches = list(re.finditer(pattern, segment))
    if not matches:
        return None, product.unit

    match = matches[-1]
    quantity = int(match.group(1))
    unit = (match.group(2) or product.unit).lower()
    if unit in {"cartons", "ctn", "ctns", "peti", "petian", "case", "cases"}:
        unit = "carton"
    elif unit in {"pcs", "piece", "pieces"}:
        unit = "piece"
    return quantity, unit


def parse_order(text: str, products: list[Product]) -> tuple[list[ParsedItem], list[str]]:
    parsed: list[ParsedItem] = []
    unmatched: list[str] = []

    for segment in _split_segments(text):
        if wants_balance(segment) and not re.search(r"\b\d+\b", segment):
            continue

        product, score = _best_product(segment, products)
        if product is None or score < 0.64:
            cleaned = " ".join(w for w in segment.split() if w not in FILLER)
            if cleaned:
                unmatched.append(segment)
            continue

        qty, unit = _extract_quantity(segment, product)
        if qty is None:
            unmatched.append(segment)
            continue

        parsed.append(ParsedItem(product=product, quantity=qty, unit=unit, segment=segment))

    return parsed, unmatched
