.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Account Invoice Import UBL
==========================

This module is an extension of the module *account_invoice_import* to add the ability to import UBL XML invoices. The `UBL (Universal Business Language) <http://ubl.xml.org/>`_ standard is a XML standard for business documents (invoices, purchase orders, etc...) created by `OASIS <https://en.wikipedia.org/wiki/OASIS_%28organization%29>`_ (Organization for the Advancement of Structured Information Standards). The UBL standard became the `ISO/IEC 19845 <http://www.iso.org/iso/catalogue_detail.htm?csnumber=66370>`_ standard in December 2015 (cf the `official announce <http://www.prweb.com/releases/2016/01/prweb13186919.htm>_`).

This module works well with `e-fff <http://www.e-fff.be/>`_ invoices as used in Belgium (e-fff invoices are UBL invoices with an embedded PDF file).

Configuration
=============

There is no configuration specific to this module. Please refer to the configuration section of the modules *account_invoice_import* and *account_tax_unece*.

Usage
=====

Refer to the usage section of the module *account_invoice_import*.

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
