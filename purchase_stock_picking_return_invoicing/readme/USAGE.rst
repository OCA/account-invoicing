Case 1: When you return to a supplier some products, and you have not yet
received the bill from the supplier

#. Go to *Purchases > Purchase > Purchase Orders > Create*.
#. Choose a supplier and add a product whose *Control Purchase Bills* is
   *On received quantities*, and input some quantity to purchase.
#. Confirm the purchase order.
#. Go to *Shipment > Validate > Apply* so as to receive the quantities ordered.
#. Press the button *Return*.
#. In the wizard *Reverse Transfer* set *Quantity* to the quantity to be
   returned. Press *Return* to complete the wizard. **IMPORTANT**: You have to
   mark "To refund (Update SO/PO)" check before pressing the button.
#. On the return picking press *Validate > Apply*.
#. Go back to the purchase order. You will notice that the field *Returned
   Qty* is now the quantity that was returned.
#. Press the button *Create Bill* to create the vendor bill.
#. The proposed vendor bill will be proposed for the difference between the
   received and the returned quantity.

Case 2: When you return to a supplier some products, and you have already
received a bill from the supplier.

#. Go to *Purchases > Purchase > Purchase Orders > Create*.
#. Choose a supplier and add a product whose *Control Purchase Bills* is
   *On received quantities*, and input some quantity to purchase.
#. Confirm the purchase order.
#. Go to *Shipment > Validate > Apply* so as to receive the quantities ordered.
#. Go back to the purchase order. Press the button *Create Bill* to create
   the vendor bill.
#. The proposed vendor bill will be proposed for the quantity received. The
   *Billing Status* is now 'No Bill to Receive'
#. Go to the original incoming shipment
#. Press the button *Return*.
#. In the wizard *Reverse Transfer* set *Quantity* to the quantity to be
   returned. Press *Return* to complete the wizard. **IMPORTANT**: You have to
   mark "To refund (Update SO/PO)" check before pressing the button.
#. On the return picking press *Validate > Apply*.
#. Go back to the purchase order. It will have  *Billing Status* as 'Waiting
   Bills'. You will notice that the field *Returned Qty* is now the quantity
   that was returned.
#. Press the button *Refunds* to create the vendor refund bill.
#. The proposed vendor refund bill will be proposed for the quantity that is
   to be refunded.
#. If you back to the purchase order, you will notice that *Billing Status*
   is now 'No Bill to Receive', even when the quantity ordered does not match
   with the quantity invoiced, because you did return some products.

Remark: If you accept that you will not claim for a refund for the quantity
returned to the supplier, just leave without checking the mark
"To refund (Update SO/PO)" on the return dialog.
