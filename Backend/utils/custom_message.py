from typing import Optional, Dict, Any
from enum import Enum

class ErrorSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlchemistException(Exception):
    """Base exception for all Alchemist application errors"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 400,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.severity = severity
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.message,
            "status_code": self.status_code,
            "severity": self.severity.value,
            "details": self.details
        }

class MindatAPIException(AlchemistException):
    """Specific exception for Mindat API errors"""
    pass

class LLMException(AlchemistException):
    """Specific exception for LLM-related errors"""
    pass