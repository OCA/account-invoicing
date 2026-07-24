Origin
~~~~~~

This module is a **functional backport** of the **Purchase Matching** feature
introduced in **Odoo 19.0 Community Edition**. The original code is part of the
Odoo ``purchase`` addon and is licensed LGPL-3 by Odoo S.A.; as required for OCA
backports, this module keeps that **LGPL-3** license.

Upstream sources (Odoo 19.0 CE):

* ``purchase.bill.line.match`` model --
  https://github.com/odoo/odoo/blob/19.0/addons/purchase/models/purchase_bill_line_match.py
* ``purchase.bill.line.match`` list view --
  https://github.com/odoo/odoo/blob/19.0/addons/purchase/views/purchase_bill_line_match_views.xml
* ``account.move.action_purchase_matching`` and
  ``account.move(.line)._add_purchase_order_lines`` --
  https://github.com/odoo/odoo/blob/19.0/addons/purchase/models/account_invoice.py
* ``bill.to.po.wizard`` ("Add to PO") --
  https://github.com/odoo/odoo/blob/19.0/addons/purchase/wizard/bill_to_po_wizard.py

Assumed differences 19.0 -> 16.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Down payments** -- 19.0 unions the ``is_downpayment`` purchase order lines
  in the matching view and copies the flag onto created bill lines. The
  ``is_downpayment`` field does not exist on ``purchase.order.line`` in 16.0 CE,
  so that ``OR`` branch of the SQL view and the flag copy are dropped. Regular
  matching is unaffected.
* **Add to PO** -- 19.0 offers an ``action_add_to_po`` button that opens a
  ``bill.to.po.wizard`` (a transient model). This flow **is** backported: from
  the matching screen the user selects vendor bill lines and clicks **Add to
  PO** to pour them into an existing or new purchase order. The wizard's
  ``action_add_to_po`` product path is backported faithfully (it keeps the
  19.0 negative-id ``active_ids`` convention to recover the account move lines,
  and inlines ``account.move.line._prepare_line_values_for_purchase`` which does
  not exist in 16.0). Only the ``action_add_downpayment`` sub-case is **not**
  backported: it depends on ``purchase.order.line.is_downpayment`` and
  ``purchase.order._create_downpayments``, which do not exist in 16.0 CE (same
  wall as the down-payment branch dropped from the matching view above).
* **PO line discount** -- ``purchase.order.line`` has no ``discount`` field in
  16.0 CE (added in 17.0+). When pouring bill lines into a purchase order, the
  bill line discount is folded into the net unit price instead of being copied.
* **OWL widgets** -- 19.0 uses the front-end widgets
  ``open_match_line_widget`` and ``monetary_no_zero``. They are replaced by a
  standard per-row **Open** button (``action_open_line``) and the standard
  ``monetary`` widget, to stay on 16.0 CE assets.
* **SQL helper** -- 19.0 builds the view with ``odoo.tools.SQL`` and
  ``_table_query`` (17.0+). 16.0 has neither, so the ``UNION`` view is created
  the 16.0 way in ``init()``.
* **ORM helpers** -- 19.0 ``recordset.grouped()`` (17.0+) and
  ``_get_records_action`` are reimplemented inline for 16.0.
* **View syntax** -- 19.0 ``<list>`` / string-valued ``invisible`` /
  ``column_invisible`` are rewritten with the 16.0 ``<tree>`` / ``attrs`` /
  ``invisible="1"`` syntax.
