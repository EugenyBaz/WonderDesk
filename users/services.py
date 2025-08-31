import stripe

from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_product(product_name):
    """
    Создает продукт в Stripe с указанным названием.
    Возвращает ID продукта.
    """
    try:
        product = stripe.Product.create(name=product_name, description="Оплата подписки.")
        return product.id
    except Exception as e:
        print(f"Ошибка при создании продукта: {e}")
        return None


def create_stripe_price(product_id, amount):
    """Создает цену в страйпе."""

    return stripe.Price.create(
        currency="rub",
        unit_amount=int(amount * 100),
        product=product_id,
    )


def create_stripe_session(price):
    """Создает сессию на оплату в страйпе."""

    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
    )

    return session.get("id"), session.get("url")
