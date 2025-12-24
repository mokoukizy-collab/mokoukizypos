from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = 0.0
    currency: str = "TWD"
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    stock: int = 0
class ProductCreate(ProductBase):
    pass
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    stock: Optional[int] = None
class ProductOut(ProductBase):
    id: int
    class Config:
        from_attributes = True
