"""
Unit tests for cleaning.py — each cleaning function gets tested against
known tricky inputs, including edge cases (missing values, ambiguous units,
unrecognized formats) that are easy to silently get wrong.

Run with: pytest tests/
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from cleaning import (
    standardize_category, parse_price, parse_weight_with_flag,
    parse_date, standardize_bool, clean_orders
)


def test_standardize_category_handles_case_and_whitespace():
    assert standardize_category("toys") == "Toys"
    assert standardize_category(" Toys ") == "Toys"
    assert standardize_category("TOYS") == "Toys"
    assert standardize_category("Art  Supplies") == "Art Supplies"
    assert standardize_category("ArtSupplies") == "Art Supplies"


def test_standardize_category_maps_known_singular_typos():
    # 'Toy' and 'Book' are real leftover variants found in the raw export —
    # this test exists specifically because a first version of this function
    # missed them (title-casing alone doesn't fix a singular/plural typo).
    assert standardize_category("Toy") == "Toys"
    assert standardize_category("book") == "Books"


def test_parse_price_handles_all_known_formats():
    assert parse_price("651.16") == 651.16
    assert parse_price("Rs.804.26") == 804.26
    assert parse_price("637.47 INR") == 637.47
    assert parse_price("1,474.40") == 1474.40


def test_parse_price_handles_missing_and_invalid():
    assert parse_price("") is None
    assert parse_price(None) is None
    assert parse_price("not a price") is None


def test_parse_weight_converts_to_grams():
    assert parse_weight_with_flag("1160g") == (1160.0, False)
    assert parse_weight_with_flag("2.87kg") == (2870.0, False)


def test_parse_weight_flags_ambiguous_bare_numbers():
    value, was_ambiguous = parse_weight_with_flag("500")
    assert value == 500.0
    assert was_ambiguous is True  # this is the important assertion —
    # a bare number's unit is genuinely unknown, and the test enforces
    # that the function admits that instead of silently guessing


def test_parse_date_handles_all_four_formats():
    assert parse_date("27/06/2025") == pd.Timestamp("2025-06-27")
    assert parse_date("2025-06-27") == pd.Timestamp("2025-06-27")
    assert parse_date("06-27-2025") == pd.Timestamp("2025-06-27")
    assert parse_date("27 Jun 2025") == pd.Timestamp("2025-06-27")


def test_parse_date_returns_none_for_unrecognized_format():
    assert parse_date("not-a-date") is None


def test_standardize_bool_handles_all_variants():
    for val in ["Yes", "yes", "Y", "y", "1", "True", "true", "TRUE"]:
        assert standardize_bool(val) is True
    for val in ["No", "no", "N", "n", "0", "False", "false", "FALSE"]:
        assert standardize_bool(val) is False


def test_standardize_bool_returns_none_for_unrecognized():
    assert standardize_bool("maybe") is None
    assert standardize_bool(None) is None


def test_clean_orders_removes_exact_duplicates():
    raw = pd.DataFrame({
        "order_id": [1, 1, 2],
        "customer_name": ["A", "A", "B"],
        "category": ["toys", "toys", "books"],
        "price": ["100", "100", "200"],
        "weight": ["500g", "500g", "1kg"],
        "order_date": ["2025-01-01", "2025-01-01", "2025-01-02"],
        "express_shipping": ["Yes", "Yes", "No"],
    })
    result = clean_orders(raw)
    assert len(result) == 2  # the exact duplicate row was dropped


def test_clean_orders_output_has_expected_columns():
    raw = pd.DataFrame({
        "order_id": [1], "customer_name": ["A"], "category": ["toys"],
        "price": ["100"], "weight": ["500g"], "order_date": ["2025-01-01"],
        "express_shipping": ["Yes"],
    })
    result = clean_orders(raw)
    assert "weight_grams" in result.columns
    assert "weight_unit_was_ambiguous" in result.columns
    assert "weight" not in result.columns  # replaced by weight_grams
