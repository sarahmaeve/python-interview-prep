def calculate_total(items):
    """Calculate the total price of all items in the cart."""
    total = 0
    for item in items:
        total += item["price"]
    return total


def apply_discount(total, percent):
    """Apply a percentage discount to the total."""
    return total - (total * percent)


def format_receipt(items, total):
    """Format a receipt string listing each item and the total."""
    lines = []
    for item in items:
        lines.append(f"{item['name']}: {item['price']}")
    lines.append(f"Total: ${total:.2f}")
    return "\n".join(lines)
