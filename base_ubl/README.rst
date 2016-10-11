.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========
Base UBL
========

This is the base module for the implementation of the `Universal Business Language (UBL) <http://ubl.xml.org/>`_ standard.  The UBL standard became the `ISO/IEC 19845 <http://www.iso.org/iso/catalogue_detail.htm?csnumber=66370>`_ standard in January 2016 (cf the `official announce <http://www.prweb.com/releases/2016/01/prweb13186919.htm>_`).

This module contains methods to generate and parse UBL files. This module doesn't do anything useful by itself, but it is used by several other modules:

* *purchase_order_ubl* that generate UBL purchase orders,
* *sale_order_import_ubl* that imports UBL sale orders.
* *account_invoice_import_ubl* that imports UBL invoices,

Configuration
=============

No configuration is needed.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

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
