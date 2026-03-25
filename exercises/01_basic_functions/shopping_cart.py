def calculate_total(items):
    """Calculate the total price of all items in the cart."""
    total = 0
    for item in items:
        total += item["price"]  # BUG: price is a string, needs float() conversion
    return total


def apply_discount(total, percent):
    """Apply a percentage discount to the total."""
    return total - (total * percent)  # BUG: should be percent / 100


def format_receipt(items, total):
    """Format a receipt string listing each item and the total."""
    lines = []
    for i in range(len(items) - 1):  # BUG: should be range(len(items))
        lines.append(f"{items[i]['name']}: ${items[i]['price']}")
    lines.append(f"Total: ${total:.2f}")
    return "\n".join(lines)
