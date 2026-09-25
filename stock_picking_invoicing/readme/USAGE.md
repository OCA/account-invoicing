To use this module, you need to:

1.  Go to your picking;
2.  If the invoice status is 'To be invoiced', a button will ask you to
    create an invoice;
3.  Into the List view, you can select many pickings and create a
    grouped invoice;
4.  If at least an invoice is created for a picking, a new "Invoicing"
    tab appears.

If an invoice (not refund) is cancelled or deleted, invoice status of
related picking is automatically updated to "To be invoiced".

Also about the cancellation of stock moves linked to invoices/bills:

- Attempt to cancel a picking linked to invoices/bills.
- If the user is not part of the group "Allow to cancel stock move
  linked to invoice/bill", an error will be raised, preventing the
  cancellation.
- Members of the group can proceed with the cancellation without
  restrictions.
