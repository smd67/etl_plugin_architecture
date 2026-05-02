"""
Data model for the ETL Plugin Architecture
"""

from typing import Generic, TypeVar
from pydantic import BaseModel

# Generic type placeholder
T = TypeVar("T")


class PluginQuery(BaseModel, Generic[T]):
    """
    Generic query classs.
    """
    data: T


class PluginResult(BaseModel, Generic[T]):
    """
    Generic plugin results class.
    """
    plugin_name: str
    plugin_data: T


class AppResult(BaseModel, Generic[T]):
    """
    Generic apps results class (merged).
    """
    data: T
