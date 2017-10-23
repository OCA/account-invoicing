.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3


Account Invoice Zero Autopay
============================

Invoices with a amount of 0 are automatically set as paid.

When an invoice has an amount of 0, Odoo still generates a
receivable/payable move line with a 0 balance.  The invoice stays as
open even if there is nothing to pay.  The user has 2 ways to set the
invoice as paid: create a payment of 0 and reconcile the line with the
payment or reconcile the receivable/payable move line with itself.
This module takes the latter approach and will directly set the invoice
as paid once it is opened.

One possible use case is that users create sales orders with price 0
to deliver free products (gifts, faulty products replenishment...),
and always stay undone due to this. Another one is when dealing with 
discount coupon codes that leads to a 0 amount sales order.

This module was named 'account_invoice_zero' before v8
 
Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20account_invoice_zero_autopay%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Pedro M. Baeza <pedro.baeza@gmail.com>
* Charbel Jacquin <charbel.jacquin@camptocamp.com>
* Jarmo Kortetjärvi <jarmo.kortetjarvi@tawasta.fi>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
