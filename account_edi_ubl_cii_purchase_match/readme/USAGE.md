1. Import a vendor bill in UBL format through: Accounting / Vendors / Bills / Upload
2. The module will automatically:
   - Extract the OrderReference from the UBL.
   - Find the matching purchase order via `partner_ref` or purchase order ref.
   - Attempt to match each UBL line with the correct purchase order line using:
     - product name,
     - supplier product name
3. When a match is found: the vendor bill line is linked to the purchase order line.
4. If no match is found:
   - Click "Select purchase line" button in invoice line 
   - Select a purchase order and a purchase order line