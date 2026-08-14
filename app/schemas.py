from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional


class UserPostRegister(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str


class UserPostLogin(BaseModel):
    email: EmailStr
    password: str


class UserGetRegister(BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr


class ProductPostMap(BaseModel):
    name: str
    buying_price: float
    selling_price: float
    model: str
    year: int
    condition: str
    fuel: str
    # created_at: str


class ProductGetMap(ProductPostMap):
    id: int


class RemainingPerProductMap(BaseModel):
    product_id: int
    product_name: str
    remaining_quantity: float


class SaleDetailsItem(BaseModel):
    product_id: int
    quantity: float


class SalePostMap(BaseModel):
    details: list[SaleDetailsItem]


class SaleGetMap(SalePostMap):
    id: int
    created_at: datetime
    updated_at: datetime


class SalePerProductMap(BaseModel):
    sale_id: int
    product_id: int
    quantity: float
    created_at: datetime


class PurchasePostMap(BaseModel):
    product_id: int
    quantity: float


class PurchaseGetMap(PurchasePostMap):
    id: int
    quantity: float
    product_id: int
    created_at: datetime
    updated_at: datetime


class SalesPerProductOut(BaseModel):
    product_id: int
    product_name: str
    total_quantity_sold: int
    total_sales_amount: float


class RemainingPerProductOut(BaseModel):
    product_id: int
    product_name: str
    remaining_quantity: int


class ProfitPerProduct(BaseModel):
    product_id: int
    product_name: str
    total_quantity_sold: int
    total_revenue: float
    total_profit: float


class ProfitPerDay(BaseModel):
    date: date
    total_profit: float


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    scopes: list[str] = []


class PaymentResponse(BaseModel):
    id: int
    sale_id: str
    merchant_request_id: Optional[str] = None
    checkout_request_id: Optional[str] = None
    trans_code: str | None
    trans_amount: float | None
    phone_paid: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class Item(BaseModel):
    id: int
    name: str
    price: float
