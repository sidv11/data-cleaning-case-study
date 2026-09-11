"""
cleaning.py — reusable, tested functions for cleaning the toy shop's messy
order export. Each function does ONE job, so it can be reused on any future
export from this same system (or a similar one) without rewriting logic
inside a notebook every time.
"""
import re
import pandas as pd


def standardize_category(raw_category: str) -> str:
    """
    Collapse inconsistent category labels ('toys', ' Toys', 'TOYS') into
    one canonical form ('Toys').

    Handles two separate kinds of messiness:
    1. Case/whitespace differences ('toys', ' TOYS ') — fixed automatically.
    2. Known typos/variants that aren't just case differences ('Toy' meaning
       'Toys', 'Book' meaning 'Books') — these can't be auto-detected safely
       (is 'Toy' a typo for 'Toys', or a genuinely different single-item
       category? only a human familiar with the data can say for sure), so
       they're handled through an explicit, human-reviewed synonym map below
       rather than guessed at silently.
    """
    if pd.isna(raw_category):
        return raw_category
    cleaned = re.sub(r"\s+", " ", raw_category.strip())
    cleaned = cleaned.title().replace("Artsupplies", "Art Supplies")
    return KNOWN_CATEGORY_SYNONYMS.get(cleaned, cleaned)


# Known singular/plural or typo variants observed in this specific export,
# confirmed by a human to mean the same category as their canonical form.
# This list grows over time as new messy exports reveal new variants —
# it's meant to be maintained, not treated as complete on day one.
KNOWN_CATEGORY_SYNONYMS = {
    "Toy": "Toys",
    "Book": "Books",
}


def parse_price(raw_price: str) -> float:
    """
    Convert a messy price string into a plain float, regardless of which
    format it was written in: '651.16', 'Rs.804.26', '637.47 INR', '1,474.40'.

    Returns None if the value is missing/unparseable, rather than crashing —
    a cleaning function should never blow up the whole pipeline on one bad row.
    """
    if raw_price is None or (isinstance(raw_price, float) and pd.isna(raw_price)) or raw_price == "":
        return None
    text = str(raw_price)
    text = text.replace("Rs.", "").replace("INR", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def parse_weight_to_grams(raw_weight: str) -> float:
    """
    Convert a messy weight string into a single standard unit: grams.
    Handles '1160g', '2.87kg', and bare numbers with no unit at all.

    For bare numbers (ambiguous unit), we assume grams — the smaller,
    more common unit in this dataset — but flag that assumption explicitly
    rather than silently guessing. See `parse_weight_with_flag` for the
    version that surfaces this uncertainty instead of hiding it.
    """
    value, _ = parse_weight_with_flag(raw_weight)
    return value


def parse_weight_with_flag(raw_weight: str):
    """
    Same as parse_weight_to_grams, but returns (value_in_grams, was_ambiguous)
    so the caller can decide how to handle rows where we had to guess the unit.
    """
    if raw_weight is None or (isinstance(raw_weight, float) and pd.isna(raw_weight)) or raw_weight == "":
        return None, False
    text = str(raw_weight).strip().lower()
    match = re.match(r"^([\d.]+)\s*(kg|g)?$", text)
    if not match:
        return None, False
    number, unit = match.groups()
    number = float(number)
    if unit == "kg":
        return number * 1000, False
    elif unit == "g":
        return number, False
    else:
        # No unit given — ambiguous. We assume grams, but flag it.
        return number, True


def parse_date(raw_date: str):
    """
    Convert any of the known date formats in this export into a single
    standard pandas Timestamp (ISO: YYYY-MM-DD).

    Handles: '27/06/2025' (DD/MM/YYYY), '2025-01-10' (already ISO),
             '08-05-2025' (MM-DD-YYYY), '08 May 2025' (DD Mon YYYY).
    """
    if raw_date is None or raw_date == "" or (isinstance(raw_date, float) and pd.isna(raw_date)):
        return None
    known_formats = ["%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d %b %Y"]
    for fmt in known_formats:
        try:
            return pd.to_datetime(raw_date, format=fmt)
        except (ValueError, TypeError):
            continue
    return None  # none of the known formats matched


def standardize_bool(raw_value: str):
    """
    Convert any of 'Yes','No','Y','N','1','0','True','False' (any case)
    into a real Python bool. Returns None for anything unrecognized,
    rather than silently guessing.
    """
    if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
        return None
    text = str(raw_value).strip().lower()
    true_values = {"yes", "y", "1", "true"}
    false_values = {"no", "n", "0", "false"}
    if text in true_values:
        return True
    elif text in false_values:
        return False
    return None


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full pipeline: applies every cleaning function above to a raw orders
    DataFrame and returns a clean one, plus drops exact duplicate rows.
    This is the single function the notebook (and any future script) calls —
    everything else in this file is a building block for this one.
    """
    clean = df.drop_duplicates().copy()

    clean["category"] = clean["category"].apply(standardize_category)
    clean["price"] = clean["price"].apply(parse_price)

    weight_results = clean["weight"].apply(parse_weight_with_flag)
    clean["weight_grams"] = weight_results.apply(lambda x: x[0])
    clean["weight_unit_was_ambiguous"] = weight_results.apply(lambda x: x[1])
    clean = clean.drop(columns=["weight"])

    clean["order_date"] = clean["order_date"].apply(parse_date)
    clean["express_shipping"] = clean["express_shipping"].apply(standardize_bool)

    return clean
