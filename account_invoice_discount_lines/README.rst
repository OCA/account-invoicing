.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================================
Transfer discounts to separate invoice lines
============================================

Upon invoice confirmation, any discounts will be transferred onto separate invoice lines, grouped by tax. This way, accounting entries will be created for the amount of discount without changing the invoice balance or the sum of taxes.

Configuration
=============

Configure a dedicated invoice product in the compay settings. Use the product accounting settings to configure the expense and revenue accounts. Note that while sale discounts are an expense and purchase discounts may count as a revenue, sale discounts will still be posted on the revenue account and purchase discounts on the expense account of the product.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

Known issues / Roadmap
======================

* Because there may be incompatibilities in the tax lines before and after rewriting the invoice lines, they will always be recomputed for invoices with discounts. Any corrections of the total tax amount will be lost.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Stefan Rijnhart <stefan@opener.amsterdam>

Do not contact contributors directly about support or help with technical issues.

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
