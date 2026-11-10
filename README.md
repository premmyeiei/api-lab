# API Testing with pytest and requests (`api-lab`)

Automated API test suite for the [QuickPizza API](https://quickpizza.grafana.com) using `pytest` and `requests`.

## Prerequisites

- Python 3.10 or newer
- `curl` (use `curl.exe` in Windows PowerShell)

## Installation

Create and activate a virtual environment, then install the dependencies from `requirements.txt`.

### macOS and Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Tests

Run the full test suite:

```bash
pytest -v
```

Save the output of a full run as a self-contained HTML report (`report.html`):

```bash
pytest -v --html=report.html --self-contained-html
```

## Input Domain Model for `POST /api/ratings` (Steps A1 & A2)

`POST /api/ratings` takes a JSON body with two fields, `pizza_id` and `stars`, and an `Authorization` token in the header. QuickPizza accepts a whole number of stars from 1 to 5, a pizza that exists, and the token of a logged-in user.

### Summary Table (Step A1)

| Characteristic | Blocks | Values in the tests |
| :--- | :--- | :--- |
| **C1 Value of stars** | below 1, 1 to 5 (base), above 5 | `0`, `3`, `6` |
| **C2 Type of stars** | whole number (base), decimal, text, missing | `3`, `3.5`, `"3"`, no field |
| **C3 Pizza** | exists (base), does not exist | a new pizza, `999999999` |
| **C4 Token** | the user's own (base), none, wrong length | from `auth`, no header, `token short` |

### Base Choice Coverage Mapping (Step A2)

Each block in the input domain model is covered by a test in `test_create_rating.py`:

| Characteristic | Block | Value in the test | Test covering the block (`test_create_rating.py`) |
| :--- | :--- | :--- | :--- |
| **C1 Value of stars** | below 1 | `0` | `test_stars_out_of_range[0]` |
| **C1 Value of stars** | 1 to 5 (base) | `3` | `test_base_choice_is_saved` |
| **C1 Value of stars** | above 5 | `6` | `test_stars_out_of_range[6]` |
| **C2 Type of stars** | whole number (base) | `3` | `test_base_choice_is_saved` |
| **C2 Type of stars** | decimal | `3.5` | `test_decimal_stars_is_refused` |
| **C2 Type of stars** | text | `"3"` | `test_text_stars_is_refused` |
| **C2 Type of stars** | missing | no `stars` field | `test_missing_stars_is_refused` |
| **C3 Pizza** | exists (base) | a new pizza (`pizza_id`) | `test_base_choice_is_saved` |
| **C3 Pizza** | does not exist | `999999999` | `test_nonexistent_pizza_is_refused` |
| **C4 Token** | the user's own (base) | from `auth` | `test_base_choice_is_saved` |
| **C4 Token** | none | no `Authorization` header | `test_rating_without_token_is_refused` |
| **C4 Token** | wrong length | `Authorization: token short` | `test_rating_with_short_token_is_refused` |
