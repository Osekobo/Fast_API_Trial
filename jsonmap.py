from pydantic import BaseModel, EmailStr


class postRegister(BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr


class getRegister(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str


class Token(BaseModel):
    token: str
    token_type: str


class getProducts(BaseModel):
    name: str
    buying_price: float
    selling_price: float


class postProducts(BaseModel):
    id: int
