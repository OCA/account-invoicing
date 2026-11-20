#. Open a vendor bill (or refund) with a vendor set.
#. Click the **Purchase Matching** smart button in the button box (visible to
   purchase users, hidden once every product line of the bill is already linked
   to a purchase order line).
#. In the list, tick the purchase order line(s) and the bill line(s) you want to
   reconcile.
#. Click **Match**:

   * bill lines are linked to the selected purchase order line of the same
     product;
   * purchase order lines without a counterpart on the bill are added to it;
   * unmatched selected bill lines are removed.

#. Selecting only purchase order lines (no bill line) and clicking **Match**
   instead creates a new draft vendor bill from those purchase order lines and
   opens it.
#. To turn bill lines into a purchase order instead, tick the bill line(s) of a
   single vendor and click **Add to PO** (visible to purchase users): a wizard
   asks for an existing purchase order of that vendor, or creates a new one. On
   confirmation the bill lines become purchase order lines (product, quantity,
   price -- converted to the order currency when needed --, taxes and unit of
   measure), the order is confirmed, and each bill line is linked back to its new
   purchase order line.
#. Adjust **Quantity** or **Price** inline if needed: the change is written back
   to the related line. Use the **Open** action on a row to jump to its purchase
   order or vendor bill.
