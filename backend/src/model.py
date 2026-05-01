from pydantic import BaseModel
from typing import Generic, TypeVar

# 1. Define the placeholder
T = TypeVar("T")

class PluginQuery(BaseModel, Generic[T]):
    data: T

class PluginResult(BaseModel, Generic[T]):
    plugin_name: str
    plugin_data: T

class AppResult(BaseModel, Generic[T]):
    data: T

class ArbitrageQuery(BaseModel):
    isbn: str
    
class BookFinderResult(BaseModel):
    isbn: str
    title: str
    author: str
    price: float
    url_text: str
    url: str

class AddAllResult(BaseModel):
    isbn: str
    title: str
    author: str
    price: float
    url_text: str
    url: str