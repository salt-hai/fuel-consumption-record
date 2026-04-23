from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None

def success_response(data: T = None, message: str = "success") -> ApiResponse:
    return ApiResponse(code=0, message=message, data=data)

def error_response(code: int, message: str) -> ApiResponse:
    return ApiResponse(code=code, message=message, data=None)
