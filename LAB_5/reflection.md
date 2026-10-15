# Lab 5: Static Code Analysis — Reflection

## 1. What is static code analysis?

Static code analysis examines source code without executing the program. It helps identify potential bugs, insecure coding patterns, maintainability problems, and style violations before the code is deployed.

## 2. What is the purpose of Pylint, Bandit, and Flake8?

- **Pylint** checks Python code quality, naming conventions, documentation, and potential programming mistakes.
- **Bandit** checks Python source code for common security risks.
- **Flake8** checks Python formatting and style, including PEP 8 conventions.

## 3. What important issues did you find?

The original Bandit report identified five findings: a deprecated PyCrypto import, a hardcoded webhook secret, use of a non-cryptographic random generator, use of `assert` for validation, and a potential cross-site scripting risk from Mako templates. Code inspection also found billing logic problems, including too many payment attempts, an invalid 150% coupon, and incorrect refund handling.

## 4. How did you fix the issues?

I replaced deprecated encryption usage with AES-GCM from the `cryptography` library, moved the webhook secret to an environment variable, used `secrets.choice()` for coupon generation, replaced assertion-based validation with explicit exceptions, and escaped invoice user input with `html.escape()`. I also corrected payment retry limits, coupon validation, billing-date handling, refund calculation, function naming, documentation, and formatting.

## 5. What did the tools report after the fixes?

The final Pylint report gave a score of 10.00/10. Bandit reported no issues, and the Flake8 after-report was empty. The program also ran successfully in the Windows virtual environment.

## 6. What did you learn from this lab?

I learned that a program can run and still contain security weaknesses, logical bugs, and style problems. Using several static analysis tools gives complementary feedback: Pylint focuses on code quality, Bandit on security, and Flake8 on style. Re-running the tools after changes helps verify that the findings have been addressed.

## 7. Why should secrets and sensitive data not be hardcoded?

Hardcoded secrets can be exposed when code is shared or pushed to a public or shared repository. Environment variables help keep configuration separate from source code. Real payment-card processing should use an appropriate compliant payment provider rather than relying on a small demonstration program.
