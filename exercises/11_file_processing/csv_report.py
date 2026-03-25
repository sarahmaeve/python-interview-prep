"""CSV Sales Report Generator -- contains 3 bugs for you to find and fix."""


def read_sales_data(filepath):
    """Read a CSV file and return a list of dicts with product, quantity, price."""
    # BUG 1: File is opened but never closed (no with statement, no .close())
    f = open(filepath, "r")
    lines = f.read().strip().split("\n")

    if len(lines) <= 1:
        return []

    header = lines[0].split(",")
    rows = []
    for line in lines[1:]:
        values = line.split(",")
        rows.append({
            "product": values[0],
            "quantity": int(values[1]),
            "price": float(values[2]),
        })
    return rows


def calculate_totals(sales_data):
    """Group by product and return dict of product -> total revenue."""
    totals = {}
    for row in sales_data:
        product = row["product"]
        revenue = row["quantity"] * row["price"]
        # BUG 2: setdefault initializes to 0, but then we overwrite instead of accumulate
        totals.setdefault(product, 0)
        totals[product] = revenue  # Should be += revenue
    return totals


def generate_report(filepath, output_path):
    """Read sales data, calculate totals, and write a summary report."""
    # BUG 3: Catches FileNotFoundError but still writes an empty report
    try:
        sales_data = read_sales_data(filepath)
    except FileNotFoundError:
        sales_data = []

    totals = calculate_totals(sales_data)

    with open(output_path, "w") as f:
        f.write("Sales Report\n")
        f.write("=" * 40 + "\n")
        for product, total in sorted(totals.items()):
            f.write(f"{product}: ${total:.2f}\n")
