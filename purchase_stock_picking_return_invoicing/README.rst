.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================
Purchase Stock Picking Return Invoicing
=======================================

This module extends the functionality of purchase orders to better manage
supplier returns and refunds.

In the purchase order you are able to display, for each line:

* Quantity to Bill, and  Quantity to Refund as separate fields. You have the
  option to create a vendor bill or a refund. In the bill or refund the
  correct quantity will be proposed, based on those fields.

* Billed Quantity and Refunded Quantity, as separate fields.

* Received Quantity and Returned Quantity, as separate fields.



Usage
=====

Case 1: When you return to a supplier some products, and you have not yet
received the bill from the supplier

#. Go to *Purchases > Purchase > Purchase Orders > Create*.
#. Choose a supplier and add a product whose *Control Purchase Bills* is *On
   received quantities*, and input some quantity to purchase.
#. Confirm the purchase order.
#. Go to *Shipment > Validate > Apply* so as to receive the quantities ordered.
#. Press the button *Reverse*.
#. In the wizard *Reverse Quantity* Set *Quantity* to the quantity to be
   returned. Press *Return* to complete the wizard.
#. On the return picking press *Validate > Apply*.
#. Go back to the purchase order. You will notice that the field *Returned
   Qty* is now the quantity that was returned. The field *Quantity to
   Bill* will show the quantity received less the quantity returned.
#. Press the button *Invoices* to create the vendor bill.
#. The proposed vendor bill will be proposed for the difference between the
   received and the returned quantity.

Case 2: When you return to a supplier some products, and you have already
received a bill from the supplier.

#. Go to *Purchases > Purchase > Purchase Orders > Create*.
#. Choose a supplier and add a product whose *Control Purchase Bills* is *On
   received quantities*, and input some quantity to purchase.
#. Confirm the purchase order.
#. Go to *Shipment > Validate > Apply* so as to receive the quantities ordered.
#. Press the button *Invoices* to create the vendor bill.
#. The proposed vendor bill will be proposed for the quantity received. The
   *Invoice Status* is now 'Invoiced'
#. Go to the original incoming shipment
#. Press the button *Reverse*.
#. In the wizard *Reverse Quantity* Set *Quantity* to the quantity to be
   returned. Press *Return* to complete the wizard.
#. On the return picking press *Validate > Apply*.
#. Go back to the purchase order. It will have  *Invoice Status* as 'Waiting
   Invoices'. You will notice that the field *Returned Qty* is now the quantity
   that was returned. The field *Quantity to Refund* is now the showing the
   quantity returned that was previously billed.
#. Press the button *Refunds* to create the vendor refund bill (since the
   field *Quantity to Invoice* is negative).
#. The proposed vendor refund bill will be proposed for the quantity that is
   to be refunded.
#. If you back to the purchase order, you will notice that *Invoice Status*
   is now 'Invoiced', even when the quantity ordered does not match with the
   quantity invoiced, because you did return some products.

Remark: As part of the 3-way match process, if you accept that you will not
claim for a refund for the quantity returned to the supplier, just set the
purchase status as 'Done' at the end of the process, and the quantity to
invoice for the items will be set to 0 (because you have accepted the
discrepancies).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/9.0

Known issues / Roadmap
======================

* The functionality of return processing with refunds is being discussed with
  Odoo here: https://github.com/odoo/odoo/issues/13974, so this addon may not
  need to be migrated to v10.

* The computation of the quantity invoiced is hacked to overcome an issue in
  one of the tests of Odoo. See https://github.com/OCA/OCB/pull/598

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
