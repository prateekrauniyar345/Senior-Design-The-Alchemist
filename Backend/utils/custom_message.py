# Backend/utils/custom_message.py
class CustomError(Exception):
    """A custom exception with a detailed message."""
    
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)
    
    def __str__(self):
        if self.code:
            return f"[Error {self.code}] {self.message}"
        return self.message
    
    def to_dict(self):
        """Convert the error details to a dictionary."""
        error_info = {"message": self.message}
        if self.code:
            error_info["code"] = self.code
        return error_info
