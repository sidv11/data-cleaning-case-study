# Data Cleaning Case Study — Toy Shop's Messy Order Export

A hands-on data cleaning project built around a deliberately messy, realistic export: mixed price formats, mixed weight units, 4 different date formats, inconsistent category spellings, messy Yes/No fields, and duplicate rows — the kind of mess a real legacy export actually produces.

The point isn't just "clean this CSV" — it's building the cleaning logic as **reusable, tested functions**, the way you'd actually want to reuse this the next time a messy export lands on your desk.

## What's in this repo

```
data-cleaning-case-study/
├── data/
│   ├── raw/
│   │   └── messy_orders.csv        ← the messy export, generated with a fixed seed (reproducible)
│   └── processed/                  ← clean_orders.csv lands here when you run the notebook
├── cleaning.py                      ← the actual deliverable: reusable, documented cleaning functions
├── tests/
│   └── test_cleaning.py             ← 12 unit tests, including edge cases the functions must not get wrong
├── generate_messy_data.py           ← reproducibly builds the messy CSV (seeded, so it's the same every run)
├── notebook.ipynb                   ← the ELI5 walkthrough — every concept explained with an analogy first
├── requirements.txt
└── README.md
```

## What each cleaning function handles

| Problem | Function | Approach |
|---|---|---|
| Inconsistent category casing/spacing (`toys`, ` Toys `, `TOYS`) | `standardize_category` | Normalize whitespace + case |
| Genuine typos, not just case (`Toy` vs `Toys`) | `standardize_category` (synonym map) | Explicit, human-reviewed synonym list — **not** auto-guessed |
| Mixed price formats (`Rs.804.26`, `637.47 INR`, `1,474.40`) | `parse_price` | Strip symbols/text, parse to float |
| Mixed weight units, some ambiguous (`1160g`, `2.87kg`, bare `500`) | `parse_weight_with_flag` | Convert to grams; **flags** ambiguous bare numbers instead of silently guessing |
| 4 different date formats | `parse_date` | Tries each known format, returns a standard ISO date |
| Messy Yes/No fields (`Y`, `1`, `TRUE`, `yes`...) | `standardize_bool` | Maps to real Python `True`/`False`, `None` if unrecognized |
| Exact duplicate rows | `clean_orders` | Drops them (double-logged, not real repeat events) |

## A real bug, left in on purpose

The first version of `standardize_category` only fixed case/whitespace — it missed that `"Toy"` (singular) needed to map to `"Toys"`, since title-casing a different word doesn't make it the right word. The test suite (`test_standardize_category_maps_known_singular_typos`) is what caught this, not eyeballing the notebook output. Fixed with an explicit synonym map, not a cleverer auto-detection rule — deciding two different-looking labels mean the same thing needs a human to confirm it, not a guess.

This is why there's a `tests/` folder at all: a cleaning pipeline you haven't tested is a cleaning pipeline you're trusting on faith.

## Running it

```bash
pip install -r requirements.txt
pytest tests/ -v          # confirm all 12 tests pass
```
Then open `notebook.ipynb` and run it top to bottom — it walks through every problem with a plain-English analogy before the code, and saves the cleaned result to `data/processed/clean_orders.csv`.

To regenerate the raw messy data from scratch (same seed, same output every time):
```bash
python generate_messy_data.py
```
