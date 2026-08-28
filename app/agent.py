from __future__ import annotations

from dataclasses import dataclass

from app.parser import normalize_text, parse_order, wants_balance
from app.schemas import AgentDecision, MessageResponse, OrderLine
from app.store import get_customer, list_products


@dataclass
class DistributorAgent:
    """Explicit agentic workflow for the first MVP."""

    def process(self, customer_id: str, message: str) -> MessageResponse:
        customer = get_customer(customer_id)
        if customer is None:
            raise KeyError(f"Unknown customer_id: {customer_id}")

        products = list_products()
        normalized = normalize_text(message)
        parsed_items, unmatched = parse_order(normalized, products)

        lines: list[OrderLine] = []
        for parsed in parsed_items:
            requested = parsed.quantity
            available = parsed.product.stock
            fulfill = min(requested, available)
            if available <= 0:
                stock_status = "out_of_stock"
            elif fulfill < requested:
                stock_status = "partial"
            else:
                stock_status = "available"

            lines.append(
                OrderLine(
                    sku=parsed.product.sku,
                    product_name=parsed.product.name,
                    requested_qty=requested,
                    available_qty=available,
                    fulfill_qty=fulfill,
                    unit=parsed.unit,
                    unit_price=parsed.product.price,
                    line_total=fulfill * parsed.product.price,
                    stock_status=stock_status,
                )
            )

        order_total = sum(line.line_total for line in lines)
        credit_available = max(customer.credit_limit - customer.outstanding_balance, 0)
        projected_exposure = customer.outstanding_balance + order_total
        minimum_payment = max(projected_exposure - customer.credit_limit, 0)

        decision = self._decide(lines, unmatched, minimum_payment)
        reply = self._compose_reply(
            customer_name=customer.name,
            balance=customer.outstanding_balance,
            balance_requested=wants_balance(normalized),
            lines=lines,
            order_total=order_total,
            minimum_payment=minimum_payment,
            decision=decision,
        )

        return MessageResponse(
            customer=customer,
            normalized_message=normalized,
            balance_requested=wants_balance(normalized),
            order_lines=lines,
            unmatched_segments=unmatched,
            order_total=order_total,
            projected_exposure=projected_exposure,
            credit_available_before_order=credit_available,
            minimum_payment_required=minimum_payment,
            decision=decision,
            suggested_reply=reply,
        )

    @staticmethod
    def _decide(lines: list[OrderLine], unmatched: list[str], minimum_payment: float) -> AgentDecision:
        reasons: list[str] = []
        actions: list[str] = []

        if not lines:
            reasons.append("No order line could be confidently extracted.")
            actions.append("Ask the customer to clarify product and quantity.")
            return AgentDecision(status="needs_review", reasons=reasons, next_actions=actions)

        if unmatched:
            reasons.append("Some message segments were not confidently understood.")
            actions.append("Review unmatched message segments before final confirmation.")

        stock_issues = [line for line in lines if line.stock_status != "available"]
        if stock_issues:
            reasons.append("One or more requested SKUs cannot be fully fulfilled from current stock.")
            actions.append("Ask customer whether partial fulfillment is acceptable.")

        if minimum_payment > 0:
            reasons.append("New order would exceed the customer's credit limit.")
            actions.append(f"Collect at least PKR {minimum_payment:,.0f} or obtain manager approval.")
            return AgentDecision(status="credit_hold", reasons=reasons, next_actions=actions)

        if stock_issues or unmatched:
            return AgentDecision(status="needs_customer_confirmation", reasons=reasons, next_actions=actions)

        reasons.append("All extracted SKUs are in stock and credit limit is respected.")
        actions.append("Present the draft order to the customer for confirmation.")
        return AgentDecision(status="ready_for_confirmation", reasons=reasons, next_actions=actions)

    @staticmethod
    def _compose_reply(
        customer_name: str,
        balance: float,
        balance_requested: bool,
        lines: list[OrderLine],
        order_total: float,
        minimum_payment: float,
        decision: AgentDecision,
    ) -> str:
        if not lines:
            return "Order samajh nahi aya. Product ka naam aur quantity dobara bhej dein, example: 5 carton Pepsi 500ml."

        item_parts: list[str] = []
        for line in lines:
            if line.stock_status == "available":
                item_parts.append(f"{line.product_name} x {line.requested_qty} carton ✅")
            elif line.stock_status == "partial":
                item_parts.append(f"{line.product_name}: {line.requested_qty} mangay, {line.fulfill_qty} available ⚠️")
            else:
                item_parts.append(f"{line.product_name}: out of stock ❌")

        parts = [f"{customer_name}: " + "; ".join(item_parts)]
        parts.append(f"Current available order total: PKR {order_total:,.0f}.")
        if balance_requested:
            parts.append(f"Previous outstanding balance: PKR {balance:,.0f}.")
        if minimum_payment > 0:
            parts.append(
                f"Credit limit exceed ho rahi hai. Order release ke liye minimum PKR {minimum_payment:,.0f} payment/manager approval required hai."
            )
        elif decision.status == "needs_customer_confirmation":
            parts.append("Please available quantity confirm kar dein.")
        else:
            parts.append("Order confirmation ke liye ready hai.")
        return " ".join(parts)
