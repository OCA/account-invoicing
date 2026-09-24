This module extends the functionality of purchase orders and vendor bills to ensure that **draft vendor bills automatically reflect the latest receivable quantities**. 

Once installed:

- When the `qty_to_invoice` on a purchase order line increases (for example, after a product reception), any linked draft invoice lines **with the auto-update option enabled** are automatically updated to include the new quantity.  
- The purchase order line's `qty_to_invoice` is reset to zero once the quantities have been added to draft invoices, preventing double billing.  

This ensures that draft invoices are always up-to-date and reduces manual adjustments, particularly in multi-shipment or electronic invoicing scenarios.

The following diagram illustrates how the module updates draft vendor bills
based on the `qty_to_invoice` of purchase order lines **only if the auto-update option is enabled**:

```
        +-----------------+
        | qty_to_invoice  |  <-- recalculated after product receptions
        +--------+--------+
                |
                v
  Check for linked draft invoice lines
    +---------------------------+
    | draft invoice lines exist?|
    +-----------+---------------+
                |Yes
                v
Check if invoice auto-update is enabled
+------------------------------------+
| move.auto_update_draft_qty == True? |
+---------------+--------------------+
                |Yes
                v
Add qty_to_invoice to draft invoice line(s)
  +-------------------------------+
  | draft invoice line quantity   |
  | += qty_to_invoice             |
  +---------------+---------------+
                  |
                  v
Reset qty_to_invoice on purchase order line
        +-----------------+
        | qty_to_invoice=0 |
        +-----------------+

```

:warning: This module is in *alpha* state. This is mostly due to the way synchronization is implemented.  
Currently, the module hooks into the `_write` method on `purchase.order.line` to detect changes to `qty_to_invoice`. This is the only way to be notified when this computed field changes.  
However, this hook operates at a low level, after all other logic related to detecting changes that imply recomputation of fields. Therefore, because the synchronization modifies the `quantity` of draft invoice lines, we need to manually invalidate and force the recomputation of `qty_to_invoice` on purchase order lines to ensure the changes are properly reflected and to avoid double counting.  
Another limitation of this approach is that the synchronization is triggered at flush time, any access to `qty_to_invoice` on purchase order lines or to `quantity` on linked draft invoice lines before the flush will return the old value in the case where the synchronization modifies them.