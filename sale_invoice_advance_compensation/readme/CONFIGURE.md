Before using the feature, configure the default values that Odoo should copy to
new sales orders.

1. Go to **Sales > Configuration > Settings > Advance**.
2. Set an **Advance Product**.

   This product is used on the advance invoice line. It is required when the
   selected payment term has advance installments.

3. Optionally set an **Advance Journal**.

   This journal is used to issue the advance invoice. If you leave it empty, Odoo
   uses the same sales journal that it would normally use for a customer invoice.

4. Set a **Compensation Journal**. It must be a **Miscellaneous** journal with
   **Is Advance Journal** enabled, belonging to the same company. This journal
   is separate from the sales journal used to issue the advance invoice.

5. Go to **Accounting > Configuration > Payment Terms**.
6. Edit or create a payment term.
7. Mark with **Advance** only the payment term lines that must generate an
   advance invoice.

   Example: for a payment term "30% advance, 70% in 30 days", mark only the 30%
   line as **Advance**.

8. Make sure the Advance Product posts to a reconcilable prepayment account,
   either through its category's down payment account or its income account.
   Fiscal position mapping must also result in a reconcilable prepayment account.
   The products sold on the order can keep their normal revenue accounts.

When a sales order is created, Odoo copies the default Advance Product and
Advance Journal and Compensation Journal from the company settings. The user
can still change them on the sales order when needed.
