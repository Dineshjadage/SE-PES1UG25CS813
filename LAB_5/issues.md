# Lab 5: Static Code Analysis — Issues and Fixes

## Tool findings and fixes

| No. | Tool / Issue | Severity or type | Description | Fix applied |
|---:|---|---|---|---|
| 1 | Bandit B413 — deprecated PyCrypto | High | The original code imported AES from the deprecated `Crypto.Cipher` package. | Replaced it with `cryptography`'s `AESGCM`, using a configured 256-bit key and a fresh random nonce for each encryption. |
| 2 | Bandit B105 — hardcoded webhook secret | Low | The webhook secret was embedded directly in the source code. | Read the secret from the `WEBHOOK_SECRET` environment variable. |
| 3 | Bandit B311 — insecure pseudo-random generator | Low | `random.choice()` was used to generate coupon codes. | Replaced it with `secrets.choice()`, which is suitable for security-sensitive randomness. |
| 4 | Bandit B101 — assertion used for validation | Low | An `assert` statement was used to validate invoice amounts. Assertions may be disabled in optimized Python. | Replaced the assertion with an explicit conditional that raises `ValueError` for negative amounts. |
| 5 | Bandit B702 — Mako template XSS risk | Medium | The original Mako invoice template rendered user input as HTML. | Removed Mako from invoice rendering and used Python's `html.escape()` to escape the user value before inserting it into the HTML. |
| 6 | Billing logic — excessive payment attempts | Bug | The original `while attempts <= MAX_ATTEMPTS` loop allowed four attempts when the maximum was three. | Changed the retry logic to stop after `MAX_ATTEMPTS` attempts. |
| 7 | Billing logic — invalid coupon percentage | Bug | The `FRIENDS150` coupon used a 150% discount and could produce a negative invoice amount. | Reject discounts outside the 0–100% range and prevent negative totals. |
| 8 | Billing logic — next billing date | Bug | Simply incrementing the month failed for December and for dates that do not exist in the next month. | Added calendar-aware month advancement and month-end handling. |
| 9 | Billing logic — refund calculation | Bug | The original refund function returned the full plan price regardless of days used. | Calculate the unused portion of a 30-day billing period and validate the number of days used. |
| 10 | Pylint — naming and documentation | Code quality | Function names used camelCase and the module/main function lacked docstrings. | Renamed functions to snake_case and added documentation strings. |
| 11 | Flake8 — style violations | Style | The original code had long lines, insufficient blank lines, and a comparison to `None` using `==`. | Reformatted code, wrapped long lines, and used `is None` where applicable. |

## Verification after fixes

- **Program execution:** `python billing_system.py` completed successfully.
- **Pylint:** 10.00/10.
- **Bandit:** No issues identified in the after-report.
- **Flake8:** The after-report was empty, indicating no reported style violations.

## Notes

The initial Bandit report identified five findings. The functional and style issues listed above were also identified by inspecting the program and its runtime output. The results above reflect the final reports captured during this lab run.
