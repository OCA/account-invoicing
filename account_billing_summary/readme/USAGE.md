Go to *Accounting → Reporting → Billing Summary*.

A wizard will open with the following filter options:

- **Date From** – Start date of the billing period (required).
- **Date To** – End date of the billing period (required).
- **Customers** – Limit the report to selected customers. Leave blank for all.
- **Companies** – Filter by company (defaults to the current company).

Click **Export to Excel** to download the `.xlsx` file.

**Excel format**

| Row | Content |
|-----|---------|
| 1 | Report title: *Billing Summary (Invoice)* |
| 2 | From Date label + date formatted as `01-JAN-2026` |
| 3 | To Date label + date formatted as `31-JAN-2026` |
| 5 | Column headers: *ref*, *Customer Name*, then one column per product |
| 6+ | One row per customer — net amount per product, or `-` if none |

Net amount = sum of all customer invoices minus any credit notes for
the same product within the selected period.
