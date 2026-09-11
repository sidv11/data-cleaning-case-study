"""
Generates a deliberately messy CSV export from our (fictional) toy shop's
old order system — the kind of export a legacy system actually produces:
inconsistent casing, mixed units, duplicate rows, messy booleans, and
multiple date formats all mixed together.
"""
import csv
import random
from datetime import date, timedelta

random.seed(7)

names = ["Aarav Sharma","Isha Patel","Rohan Mehta","Mira Kulkarni","Kabir Singh",
         "Ananya Rao","Vivaan Joshi","Diya Nair","Arjun Reddy","Sara Khan"]

# Deliberately inconsistent category labels for the SAME underlying categories
category_variants = {
    "Toys":       ["Toys", "toys", "TOYS", " Toys", "Toy"],
    "Books":      ["Books", "books", "BOOKS", "Book "],
    "Games":      ["Games", "games", " Games"],
    "Art Supplies": ["Art Supplies", "art supplies", "ArtSupplies", "Art  Supplies"],
}

# Deliberately inconsistent "yes/no" style values for express shipping
bool_variants = ["Yes","No","Y","N","yes","no","1","0","True","False","TRUE","FALSE"]

# Deliberately inconsistent date formats
def random_date_string():
    d = date(2025,1,1) + timedelta(days=random.randint(0,300))
    fmt = random.choice(["%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d %b %Y"])
    return d.strftime(fmt)

def random_price_string():
    val = round(random.uniform(99, 1500), 2)
    style = random.choice(["plain", "rupee_symbol", "rupee_word", "comma_thousands"])
    if style == "plain":
        return str(val)
    elif style == "rupee_symbol":
        return f"Rs.{val}"
    elif style == "rupee_word":
        return f"{val} INR"
    else:
        return f"{val:,.2f}"

def random_weight_string():
    # Sometimes in grams, sometimes kg, sometimes just a bare number (unit unknown)
    style = random.choice(["g", "kg", "bare"])
    if style == "g":
        return f"{random.randint(50, 3000)}g"
    elif style == "kg":
        return f"{round(random.uniform(0.05, 3.0), 2)}kg"
    else:
        return str(random.randint(1, 3000))  # ambiguous unit — could be g or kg

rows = []
order_id = 1001
for _ in range(140):
    cat = random.choice(list(category_variants.keys()))
    row = {
        "order_id": order_id,
        "customer_name": random.choice(names),
        "category": random.choice(category_variants[cat]),
        "price": random_price_string(),
        "weight": random_weight_string(),
        "order_date": random_date_string(),
        "express_shipping": random.choice(bool_variants),
    }
    rows.append(row)
    order_id += 1

# Inject some exact duplicate rows (same order double-logged by the old system)
for _ in range(8):
    rows.append(dict(random.choice(rows)))

# Inject a few rows with missing values
for _ in range(6):
    r = dict(random.choice(rows))
    field = random.choice(["price", "weight", "customer_name"])
    r[field] = ""
    rows.append(r)

random.shuffle(rows)

with open("data/raw/messy_orders.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id","customer_name","category",
                                            "price","weight","order_date","express_shipping"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} deliberately messy rows to data/raw/messy_orders.csv")
