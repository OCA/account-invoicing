Use the module from the sales order.

1. Create a sales order.
2. Select a payment term that has one or more lines marked as **Advance**.
3. Check the **Advance Product** and, if needed, the **Advance Journal** in the
   invoicing information of the sales order.
4. Confirm the sales order.

   Odoo creates the advance lines in the **Advances** tab. These lines are only a
   plan at this point; no accounting entry is created yet.

5. Open the **Advances** tab.
6. Click **Create Advance Invoice** for the advance that must be charged.

   Odoo creates a normal customer invoice for the advance amount.

7. Post the advance invoice.
8. Register the customer's payment on that advance invoice, using the standard
   Odoo payment flow.
9. Later, create the regular customer invoice from the sales order.
10. In the invoice creation wizard, keep **Apply Advance Compensation** enabled
    if the paid advance should be used automatically.
11. Post the regular invoice.

After the regular invoice is posted, Odoo creates the compensation entry and
reconciles the paid advance with the regular invoice. The open amount of the
regular invoice is reduced by the advance amount that was already paid.

If the wizard option is disabled, no automatic compensation is created. The
advance can still be reconciled manually later.

Important: automatic compensation only applies to advances created from payment
term lines marked as **Advance**. Other customer prepayments are ignored by this
sale order flow and remain manual, as in standard Odoo.
