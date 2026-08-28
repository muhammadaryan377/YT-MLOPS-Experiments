from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class Product(BaseModel):
    sku: str
    name: str
    aliases: list[str]
    unit: str = "carton"
    price: float
    stock: int


class Customer(BaseModel):
    id: str
    name: str
    phone: str
    outstanding_balance: float = 0
    credit_limit: float = 0


class OrderLine(BaseModel):
    sku: str
    product_name: str
    requested_qty: int = Field(ge=1)
    available_qty: int = Field(ge=0)
    fulfill_qty: int = Field(ge=0)
    unit: str
    unit_price: float
    line_total: float
    stock_status: Literal["available", "partial", "out_of_stock"]


class MessageRequest(BaseModel):
    customer_id: str
    message: str = Field(min_length=1)


class AgentDecision(BaseModel):
    status: Literal[
        "ready_for_confirmation",
        "needs_customer_confirmation",
        "credit_hold",
        "needs_review",
    ]
    reasons: list[str]
    next_actions: list[str]


class MessageResponse(BaseModel):
    customer: Customer
    normalized_message: str
    balance_requested: bool
    order_lines: list[OrderLine]
    unmatched_segments: list[str]
    order_total: float
    projected_exposure: float
    credit_available_before_order: float
    minimum_payment_required: float
    decision: AgentDecision
    suggested_reply: str
