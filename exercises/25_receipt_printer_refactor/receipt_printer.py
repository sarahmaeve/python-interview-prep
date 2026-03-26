"""Receipt printer module.

This code is CORRECT but intentionally messy. All tests pass.
Your job: refactor without breaking any tests.
"""


def print_receipt(items, tax_rate, discount_code, include_header=True):
    if not items:
        raise ValueError("items cannot be empty")
    for i in items:
        if "name" not in i or "price" not in i or "quantity" not in i:
            raise ValueError("each item must have name, price, and quantity")

    if discount_code not in ("SAVE10", "BULK50", "NONE", ""):
        raise ValueError(f"unknown discount code: {discount_code!r}")

    t = 0
    for i in items:
        t = t + i["price"] * i["quantity"]

    d = 0
    if discount_code == "SAVE10":
        d = t * 0.1
    elif discount_code == "BULK50":
        if t > 50:
            d = 5.00
        else:
            d = 0

    t2 = t - d
    x = t2 * tax_rate

    if t >= 100:
        s = 0
    else:
        s = 5.99

    total = t2 + x + s

    lines = []
    if include_header:
        lines.append("=" * 40)
        lines.append("           RECEIPT")
        lines.append("=" * 40)
        lines.append(f"{'ITEM':<20} {'QTY':>4} {'PRICE':>8} {'EXT':>8}")
        lines.append("-" * 40)
        for i in items:
            ext = i["price"] * i["quantity"]
            lines.append(f"{i['name']:<20} {i['quantity']:>4} ${i['price']:>7.2f} ${ext:>7.2f}")
        lines.append("-" * 40)
        lines.append(f"{'Subtotal':<30} ${t:>7.2f}")
        if d > 0:
            if discount_code == "SAVE10":
                lines.append(f"{'Discount (SAVE10)':<30} -${d:>6.2f}")
            elif discount_code == "BULK50":
                lines.append(f"{'Discount (BULK50)':<30} -${d:>6.2f}")
        lines.append(f"{'Tax':<30} ${x:>7.2f}")
        if s == 0:
            lines.append(f"{'Shipping':<30} {'FREE':>8}")
        else:
            lines.append(f"{'Shipping':<30} ${s:>7.2f}")
        lines.append("=" * 40)
        lines.append(f"{'TOTAL':<30} ${total:>7.2f}")
        lines.append("=" * 40)
    else:
        lines.append(f"{'ITEM':<20} {'QTY':>4} {'PRICE':>8} {'EXT':>8}")
        lines.append("-" * 40)
        for i in items:
            ext = i["price"] * i["quantity"]
            lines.append(f"{i['name']:<20} {i['quantity']:>4} ${i['price']:>7.2f} ${ext:>7.2f}")
        lines.append("-" * 40)
        lines.append(f"{'Subtotal':<30} ${t:>7.2f}")
        if d > 0:
            if discount_code == "SAVE10":
                lines.append(f"{'Discount (SAVE10)':<30} -${d:>6.2f}")
            elif discount_code == "BULK50":
                lines.append(f"{'Discount (BULK50)':<30} -${d:>6.2f}")
        lines.append(f"{'Tax':<30} ${x:>7.2f}")
        if s == 0:
            lines.append(f"{'Shipping':<30} {'FREE':>8}")
        else:
            lines.append(f"{'Shipping':<30} ${s:>7.2f}")
        lines.append(f"{'TOTAL':<30} ${total:>7.2f}")

    return "\n".join(lines)
