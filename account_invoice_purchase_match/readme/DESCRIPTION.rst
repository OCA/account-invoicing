This module is a backport from Odoo SA and as such, it is not included in the
OCA CLA. That means we do not have a copy of the copyright on it like all other
OCA modules.

This module is a **functional backport to Odoo 16.0 Community Edition** of the
**Purchase Matching** feature shipped in **Odoo 19.0 Community Edition** (addon
``purchase``, model ``purchase.bill.line.match``).

It lets an accountant reconcile the lines of vendor bills with the lines of the
vendor's purchase orders from a single dedicated screen, instead of editing the
bill line by line.

From a vendor bill (or refund), a **Purchase Matching** smart button opens a
list that is a read-only ``UNION`` of:

* the vendor's *open* purchase order lines (confirmed orders still to invoice),
  and
* the *unlinked* product lines of vendor bills of that vendor.

On that screen the user selects rows and clicks **Match**. Faithfully to the
upstream ``action_match_lines``:

* each selected bill line is linked to the first selected purchase order line of
  the same product through the standard ``purchase_line_id`` field;
* if only purchase order lines are selected (no bill line), a brand new draft
  vendor bill is created from them;
* the remaining selected purchase order lines are added to the bill being
  matched, and the unmatched selected bill lines are removed, when a single bill
  is involved.

The screen also offers an **Add to PO** action (backport of the 19.0
``bill.to.po.wizard``): the user ticks vendor bill lines of a single vendor and
pours them into an existing purchase order or a brand new one, which is then
confirmed and linked back to the bill lines. Only the product path of the
wizard is backported; the down-payment sub-case (``action_add_downpayment``) is
not, as it relies on ``purchase.order.line.is_downpayment`` which is absent in
16.0 CE.

The **Quantity** and **Price** columns are editable and write straight back to
the underlying purchase order line / bill line, and an **Open** action on each
row jumps to the related purchase order or vendor bill.
