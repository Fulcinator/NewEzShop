from app.models.errors.app_error import AppError

class BalanceError(AppError):
    def __init__(self, message: str):
        super().__init__(code=421, name="BalanceError", message=message)
