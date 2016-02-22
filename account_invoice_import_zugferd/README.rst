.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Account Invoice Import ZUGFeRD
==============================

This module is an extension of the module *account_invoice_import* to add the ability to import ZUGFeRD invoices. The `ZUGFeRD <http://www.pdflib.com/knowledge-base/pdfa/zugferd-invoices/>`_ standard is a standard based on `CII <http://tfig.unece.org/contents/cross-industry-invoice-cii.htm>`_ (Cross-Industry Invoice) for electronic invoicing. A ZUGFeRD invoice is a PDF invoice with an embedded XML file that carries structured information about the invoice.

Installation
============

This module requires the Python library *pdfminer*. To install it, run:

.. code::

  sudo pip install pdfminer

Configuration
=============

There is no configuration specific to this module. Please refer to the configuration section of the modules *account_invoice_import* and *base_zugferd*.

Usage
=====

Refer to the usage section of the module *account_invoice_import*.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20account_invoice_import_zugferd%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
