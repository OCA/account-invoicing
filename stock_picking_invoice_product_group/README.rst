.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================
Invoices created from picking grouped by product
================================================

This module allows you to group invoices generated from picking by product
or by product category.
This is possible by selecting the related option in the wizard used
for creating draft invoices.

Example
--------

Created the following pickings:

1. picking_1 - partner_1
    1. product_A - category_1
    2. product_B - category_2
2. picking_2 - partner_2
    1. product_C - category_2
    2. product_D - category_3
3. picking_3 - partner_1
    1. product_C - category_2
    2. product_D - category_3
    3. product_A - category_1

Selecting option 'Group by product category' I get the following invoices:

1. invoice_1 - partner_1
    1. product_A - category_1 --> picking_1
    2. product_A - category_1 --> picking_3
2. invoice_2 - partner_1
    1. product_B - category_2 --> picking_1
    2. product_C - category_2 --> picking_3
3. invoice_3 - partner_1
    1. product_D - category_3 --> picking_3
4. invoice_4 - partner_2
    1. product_C - category_2 --> picking_2
5. invoice_5 - partner_2
    1. product_D - category_3 --> picking_2

On the contrary if I select option 'Group by product' I get the following
invoices:

1. invoice_1 - partner_1
    1. product_A - category_1 --> picking_1
    2. product_A - category_1 --> picking_3
2. invoice_2 - partner_1
    1. product_B - category_2 --> picking_1
3. invoice_3 - partner_1
    1. product_C - category_2 --> picking_3
4. invoice_4 - partner_1
    1. product_D - category_3 --> picking_3
5. invoice_5 - partner_2
    1. product_C - category_2 --> picking_2
6. invoice_6 - partner_2
    1. product_D - category_3 --> picking_2

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account_invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20stock_picking_invoice_product_group%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Alex Comba <alex.comba@agilebg.com>

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
