from __future__ import annotations

from copy import deepcopy
from app.schemas import Customer, Product


_PRODUCTS: list[Product] = [
    Product(
        sku="PEPSI-500ML",
        name="Pepsi 500ml",
        aliases=["pepsi 500ml", "pepsi 500 ml", "pepsi"],
        price=3200,
        stock=42,
    ),
    Product(
        sku="DEW-500ML",
        name="Mountain Dew 500ml",
        aliases=["mountain dew 500ml", "mountain dew", "dew 500ml", "dew"],
        price=3300,
        stock=20,
    ),
    Product(
        sku="STING-250ML",
        name="Sting 250ml",
        aliases=["sting 250ml", "sting"],
        price=3800,
        stock=1,
    ),
    Product(
        sku="COKE-1.5L",
        name="Coca-Cola 1.5L",
        aliases=["coca cola 1.5l", "coca-cola 1.5l", "coke 1.5l", "coke"],
        price=2900,
        stock=18,
    ),
    Product(
        sku="SPRITE-1.5L",
        name="Sprite 1.5L",
        aliases=["sprite 1.5l", "sprite 1.5 l", "sprite"],
        price=2850,
        stock=12,
    ),
]

_CUSTOMERS: dict[str, Customer] = {
    "ali-general-store": Customer(
        id="ali-general-store",
        name="Ali General Store",
        phone="+92-300-0000001",
        outstanding_balance=42000,
        credit_limit=50000,
    ),
    "city-mart": Customer(
        id="city-mart",
        name="City Mart",
        phone="+92-300-0000002",
        outstanding_balance=10000,
        credit_limit=100000,
    ),
}


def list_products() -> list[Product]:
    return deepcopy(_PRODUCTS)


def get_customer(customer_id: str) -> Customer | None:
    customer = _CUSTOMERS.get(customer_id)
    return customer.model_copy(deep=True) if customer else None
