from app.models.errors.app_error import AppError

class BalanceError(AppError):
    def __init__(self, message: str):
        super().__init__(message, 421)
