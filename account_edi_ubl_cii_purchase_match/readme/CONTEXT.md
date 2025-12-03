In the standard behavior, when importing a vendor bill from a UBL document:

- If a Purchase Order is found, **all imported UBL lines are replaced** by 
the Purchase Order lines.
- This causes a **loss of original UBL data**, such as:
  - line-level descriptions,
  - quantities,
  - pricing,
  - tax information received from the supplier.
- Additionally, the standard flow performs **no matching based on product labels**, 
so incorrect PO lines may be added if PO content does not reflect what is 
actually on the invoice.
