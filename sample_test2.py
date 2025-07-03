import uuid
from typing import List, Optional
from datetime import datetime

# Constants
TAX_RATE = 0.18
DEFAULT_CURRENCY = "INR"


class Product:
    """A simple product in the e-commerce system."""

    def __init__(self, name: str, price: float, quantity: int = 1):
        self.id = uuid.uuid4()
        self.name = name
        self.price = price
        self.quantity = quantity

    def total_price(self) -> float:
        return self.price * self.quantity

    def __repr__(self):
        return f"<Product {self.name} x {self.quantity} - ₹{self.total_price():.2f}>"


class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        self.created_at = datetime.now()

    def __repr__(self):
        return f"<User {self.username}>"


class Order:
    """Handles orders in the system."""

    def __init__(self, user: User, products: List[Product]):
        self.id = uuid.uuid4()
        self.user = user
        self.products = products
        self.created_at = datetime.now()
        self.status = "Pending"

    def subtotal(self) -> float:
        return sum(p.total_price() for p in self.products)

    def tax(self) -> float:
        return self.subtotal() * TAX_RATE

    def total(self) -> float:
        return self.subtotal() + self.tax()

    def summary(self) -> str:
        lines = [f"Order Summary for {self.user.username}:"]
        for p in self.products:
            lines.append(f" - {p.name} x {p.quantity}: ₹{p.total_price():.2f}")
        lines.append(f"Subtotal: ₹{self.subtotal():.2f}")
        lines.append(f"Tax: ₹{self.tax():.2f}")
        lines.append(f"Total: ₹{self.total():.2f}")
        return "\n".join(lines)


class PaymentProcessor:
    @staticmethod
    def process_payment(order: Order, method: str) -> bool:
        print(f"Processing {method} payment for Order {order.id}")
        # Simulate success
        return True

    @classmethod
    def supported_methods(cls) -> List[str]:
        return ["credit_card", "debit_card", "upi", "netbanking"]


def send_confirmation_email(user: User, order: Order):
    print(f"Sending email to {user.email} for Order {order.id}")


def apply_discount(order: Order, discount_rate: float = 0.10) -> float:
    """Apply discount on subtotal."""
    subtotal = order.subtotal()
    discount = subtotal * discount_rate
    return subtotal - discount


def track_order(order_id: uuid.UUID) -> Optional[str]:
    # Simulated order tracking
    return f"Order {order_id} is out for delivery."


def safe_process(order: Order):
    try:
        if not PaymentProcessor.process_payment(order, "upi"):
            raise Exception("Payment failed!")
        send_confirmation_email(order.user, order)
        print("Order processed successfully.")
    except Exception as e:
        print(f"Order failed: {str(e)}")


# Main
if __name__ == "__main__":
    # Sample data
    user = User("prisha_gupta", "prisha@example.com")
    items = [
        Product("Prada Handbag", 95000, 1),
        Product("Titan Watch", 8000, 2),
    ]
    order = Order(user, items)

    print(order.summary())
    discounted_total = apply_discount(order)
    print(f"Total after discount: ₹{discounted_total:.2f}")

    safe_process(order)
    print(track_order(order.id))
