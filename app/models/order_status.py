from enum import Enum

class OrderStatus(str, Enum):
    ISSUED = "ISSUED"
    PAYED = "PAYED"
    COMPLETED = "COMPLETED"
