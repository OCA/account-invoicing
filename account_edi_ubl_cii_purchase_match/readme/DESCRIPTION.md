This module extends the UBL vendor bill import process to improve how vendor
bill lines are linked to purchase order lines.

Instead of replacing the imported UBL lines with the purchase order lines
(standard behavior), this module:

1. **Reads the OrderReference** in the UBL document.
2. **Identifies the corresponding Purchase Order** using the vendor reference
(`partner_ref`) or the purchase order ref.
3. **Matches each UBL line** with a purchase order line based on:
   - product name,
   - supplier product name

4. **Links the vendor bill line** to the matched PO line
5. When a user manually selects a purchase order line from the bill:
   - the system stores the supplier product name,
   - future imports will auto-match using that supplier information.

This ensures accurate line-level linking while preserving the supplier’s
invoice data.