Unit rounded invoice (`Swedish rounding`_)
==========================================

Add a parameter to give a unit for rounding such as CHF 0.05 for Swiss
invoices

In Settings -> Configuration -> Accounting you will find 2 new types of
rounding

- `Swedish Round globally`

  To round your invoice total amount, this option will do the adjustment in
  the most important tax line of your invoice.

- `Swedish Round by adding an invoice line`

  To round your invoice total amount, this option create a invoice line without
  taxes on it. This invoice line is tagged as `is_rounding`

You can choose the account on which the invoice line will be written

.. _Swedish rounding : https://en.wikipedia.org/wiki/Swedish_rounding

In the supplier invoice, you can also set a flag (inherited by the selected partner),
in order to round supplier invoices too.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20account_invoice_rounding%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

Yannick Vaucher

Nicola Malcontenti <nicola.malcontenti@agilebg.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
