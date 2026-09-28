1. Go to **Accounting → Configuration → Taxes**
2. Open or create a tax
3. Set the field **Allowed Account Prefixes**

This field accepts a comma-separated list of account code prefixes.

Examples:
- `60` → tax allowed only for accounts starting with 60
- `60,61` → tax allowed for accounts starting with 60 or 61
- `2,60,61` → tax allowed for investments and goods/services accounts
- spaces are ignored (`60, 61` is valid)
- leave empty → tax allowed for all accounts
