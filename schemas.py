from pydantic import BaseModel

GetProduct(Base):
    name: str
    buying_price: int
    selling_price: int
