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


def validate_quantity(value: str) -> bool:
    """Return whether a quantity is a positive integer string."""
    return value.isdigit() and int(value) > 0


def validate_price(value: str) -> bool:
    """Return whether a price is a non-negative integer string."""
    return value.lstrip("-").isdigit() and int(value) >= 0


def validate_line(line: dict[str, str], seen_skus: set[str]) -> str | None:
    """Return a reason when one order line is invalid."""
    for key in REQUIRED_LINE_KEYS:
        if key not in line:
            return "missing line key"
    if not line["sku"]:
        return "empty sku"
    if line["sku"] in seen_skus:
        return "duplicate sku"
    seen_skus.add(line["sku"])
    if not validate_quantity(line["qty"]):
        return "invalid quantity"
    if not validate_price(line["unit_price_kopecks"]):
        return "invalid price"
    return None


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "empty order"

    seen_skus: set[str] = set()
    for line in lines:
        reason = validate_line(line, seen_skus)
        if reason is not None:
            return reason

    if promo_code and promo_code not in PROMO_CODES:
        return "unknown promo code"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "unsupported city"

    return None


def order_subtotal(lines: list[dict[str, str]]) -> tuple[int, int]:
    """Return the subtotal and total quantity for validated lines."""
    subtotal = 0
    total_qty = 0
    for line in lines:
        qty = int(line["qty"])
        subtotal += qty * int(line["unit_price_kopecks"])
        total_qty += qty
    return subtotal, total_qty


def discount_percent(total_qty: int, promo_code: str) -> int:
    """Return the larger applicable discount, limited by the configured cap."""
    result = 0
    for threshold, percentage in TIER_DISCOUNTS:
        if total_qty >= threshold:
            result = percentage
    promo_percent = PROMO_CODES.get(promo_code, 0)
    if promo_percent > result:
        result = promo_percent
    if result > MAX_DISCOUNT_PERCENT:
        result = MAX_DISCOUNT_PERCENT
    return result


def order_base(subtotal: int, discount_pct: int, shipping_city: str) -> int:
    """Return the discounted subtotal with applicable shipping."""
    discount = percent_of(subtotal, discount_pct)
    base = subtotal - discount
    if shipping_city and base < FREE_DELIVERY_FROM_KOPEKS:
        base += SHIPPING_KOPEKS
    return base


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None

    subtotal, total_qty = order_subtotal(lines)
    discount_pct = discount_percent(total_qty, promo_code)
    base = order_base(subtotal, discount_pct, shipping_city)
    vat = percent_of(base, VAT_PERCENT)
    return base + vat
