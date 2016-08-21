.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============
Base ZUGFeRD
============

This is the base module for the implementation of the `ZUGFeRD <http://www.pdflib.com/knowledge-base/pdfa/zugferd-invoices/>`_ standard. It is a standard based on `CII <http://tfig.unece.org/contents/cross-industry-invoice-cii.htm>`_ (Cross-Industry Invoice) for electronic invoicing. The great idea of the ZUGFeRD standard is to embed an XML file inside the PDF invoice to carry structured information about the invoice.


Configuration
=============

To configure this module, you need to:

* go to the menu *Sales > Configuration > Units of Measures* and check the *UNECE Code* for the units of measures that you use in customer invoices/refunds.
* go to the menu *Accounting > Configuration > Taxes > Taxes* and, for each tax that you may use in customer invoices/refunds, set a *UNECE Type Code* and a *UNECE Category Code*.
* go to the menu *Accouting > Configuration > Miscellaneous > Payment Export Types* and assign a *UNECE Code* to the payment types that are selected in the payment modes that you use in customer invoices/refunds.

Usage
=====

This module doesn't do anything by itself, but it is used by 2 other modules:

* account_invoice_zugferd that generate ZUGFeRD customer invoices/refunds,
* account_invoice_import_zugferd that imports ZUGFeRD supplier invoices/refunds.


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
