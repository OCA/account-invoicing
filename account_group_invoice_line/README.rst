.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Account Group Invoice Lines
===========================

This module was written to extend the option *Group Invoice Lines* of the journal. With this module, you can choose to group the account move lines generated when you validate an invoice per account, instead of grouping per product.

Configuration
=============

To configure this module, go to the menu *Accounting > Configuration > Journals > Journals* and select a sale or purchase journal. On the form view of the journal, you have an option *Group Invoice Lines*. If you activate this option, you will see a new option **Group by** with two possible values:

 * **by Product**: the account move lines generated when you validate an invoice will be grouped by product, account, analytic account, analytic tags and tax (this is the behavior when this module is not installed)

 * **by Account**: the account move lines will be grouped by account, analytic account, analytic tags and tax, without taking into account the product.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Sébastien LANGE <sebastien.lange@syleam.fr>
* Alexis de Lattre <alexis.delattre@akretion.com>

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
