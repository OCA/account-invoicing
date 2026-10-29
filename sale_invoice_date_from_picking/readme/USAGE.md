- Create a Sale Order with a storable product.
- Validate the delivery.
- Create the invoice.
- The invoice date and the accounting date will be taken from the fields on the delivery
  order, as specified in the settings.

Odoo recomputes the accounting date from the invoice date whenever the invoice date
changes, so the accounting date from the delivery order is kept only if the invoice date
is also set when the invoice is created (for example with 'Picking Date for Invoice'):

- If the invoice date is empty, Odoo sets it to today on posting, and the accounting date
  becomes today as well.
- If you change the invoice date of a draft invoice, set the accounting date again
  afterwards.
- Credit notes created from the sales order (for example after a return) do not keep the
  accounting date, as Odoo recomputes it when it turns the invoice into a credit note.

The currency rate of the invoice is still based on the invoice date.
