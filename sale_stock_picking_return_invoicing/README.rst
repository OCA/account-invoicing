.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Refund Returned Pickings from Sales Orders
==========================================

This module extends the functionality of sales orders to support marking some
returned pickings as "To refund in Sale Order" and to allow you to create
invoices deducting the products that are returned and refunded. Also allows to
modify stock move field to_refund_so after it has been confirmed.

Usage
=====

To use this module, when some customer returns some refundable products to you
before you created an invoice, you need to:

#. Go to *Sales > Sales Orders > Create*.
#. Choose a customer and add a product whose *Invoicing Policy* is *Delivered
   quantities*, and input some quantity to sell.
#. Confirm the sale.
#. Go to *Delivery > Validate > Apply > Reverse*.
#. Set *Quantity* to a lower quantity than the sold one, and enable
   *To Refund*.
#. Press *Return > Validate > Apply*.
#. Go back to the sale order.
#. Press *Create Invoice > Invoiceable lines > Create and View Invoices*.
#. The created invoice's amount will be the difference between the delivered
   and the returned quantity.

To use this module, when some customer returns some refundable products to you
after you created an invoice, you need to:

#. Go to *Sales > Sales Orders > Create*.
#. Choose a customer and add a product whose *Invoicing Policy* is *Delivered
   quantities*, and input some quantity to sell.
#. Confirm the sale.
#. Go to *Delivery > Validate > Apply*.
#. Return to the sale order.
#. Press *Create Invoice > Invoiceable lines > Create and View Invoices*.
#. The created invoice's amount is the same you sold.
#. Return to the sale order.
#. Go to *Delivery > Reverse*.
#. Set *Quantity* to a lower quantity than the sold one, and enable
   *To Refund*.
#. Press *Return > Validate > Apply*.
#. Return to the sale order.
#. Press *Create Invoice > Invoiceable lines (deduct down payments) >
   Create and View Invoices*.
#. A refund is created for the quantity you returned before.

For allowing to refund quantities after the picking has been confirmed, you can
change the value of 'Refund Options' field.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/9.0

Known issues / Roadmap
======================

* This addon is a pseudobackport of a functionality that exists natively in
  v10, plus a fix for https://github.com/odoo/odoo/issues/13974, so this addon
  will never have to be migrated to v10.

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

* Jairo Llopis <jairo.llopis@tecnativa.com>
* Sergio Teruel <sergio.teruel@tecnativa.com>

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
