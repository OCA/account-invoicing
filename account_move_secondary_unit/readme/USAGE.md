To use this module, you need to:

1. Enable *Units of Measure* under Settings > Inventory (or Purchase/Sales).
2. Go to a product form, and add at least one secondary unit of measure with a
   conversion factor.
3. Create an invoice or bill for that product.

On the invoice/bill line, you will see the following additional columns (toggle
them via the optional columns button if hidden):

- **Secondary Qty**: Changing this value automatically recalculates the primary quantity
  based on the conversion factor.
- **Second unit**: The secondary unit of measure to use.
- **Secondary Price**: Automatically computed from the unit price and the conversion
  factor. Editing it updates the unit price accordingly.

For printed/PDF invoices, you can configure how quantities and prices are displayed
under Settings > General Settings > Secondary UoM:

- *Primary*: Only the primary unit is shown (default).
- *Secondary*: Only the secondary unit quantity and price are shown.
- *Both*: Both primary and secondary values are shown.
