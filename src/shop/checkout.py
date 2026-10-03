from shop.money import percent_of

"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "empty order"

    seen_skus = set()
    for line in lines:
        for key in REQUIRED_LINE_KEYS:
            if key not in line:
                return "missing line key"
        if not line["sku"]:
            return "empty sku"
        if line["sku"] in seen_skus:
            return "duplicate sku"
        seen_skus.add(line["sku"])
        if not line["qty"].isdigit():
            return "invalid quantity"
        if int(line["qty"]) <= 0:
            return "invalid quantity"
        if not line["unit_price_kopecks"].lstrip("-").isdigit():
            return "invalid price"
        if int(line["unit_price_kopecks"]) < 0:
            return "invalid price"

    if promo_code and promo_code not in PROMO_CODES:
        return "unknown promo code"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "unsupported city"

    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None

    subtotal = 0
    total_qty = 0
    for line in lines:
        qty = int(line["qty"])
        subtotal += qty * int(line["unit_price_kopecks"])
        total_qty += qty

    discount_percent = 0
    for threshold, percentage in TIER_DISCOUNTS:
        if total_qty >= threshold:
            discount_percent = percentage

    promo_percent = PROMO_CODES.get(promo_code, 0)
    if promo_percent > discount_percent:
        discount_percent = promo_percent
    if discount_percent > MAX_DISCOUNT_PERCENT:
        discount_percent = MAX_DISCOUNT_PERCENT

    discount = percent_of(subtotal, discount_percent)
    base = subtotal - discount
    if shipping_city and base < FREE_DELIVERY_FROM_KOPEKS:
        base += SHIPPING_KOPEKS
    vat = percent_of(base, VAT_PERCENT)
    total = base + vat
    return total
