.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Account Invoice PDF Import
==========================

This module has been started by lazy accounting users who hate enter they supplier invoices manually in Odoo. As ERP consultants, we have a number of supplier invoices to enter regularly in the system from the same suppliers : phone bill, Internet access, train tickets, etc. Most of these invoices are available as PDF. We dream that we would be able to automatically extract from the PDF the required information to enter the invoice as supplier invoice in Odoo.

In the future, we believe we will have structured information embedded inside the metadata of PDF invoices. There are 2 main standards for electronic invoicing :

* `CII <>`_ (Cross-Industry Invoice) developped by `UN/CEFACT <http://www.unece.org/cefact>`_ United Nations Centre for Trade Facilitation and Electronic Business
* `UBL <http://ubl.xml.org/>`_ (Universal Business Language) developped by `OASIS <https://www.oasis-open.org/>`_ (Organization for the Advancement of Structured Information Standards)

For example, there is already a standard in Germany called `ZUGFeRD <http://www.pdflib.com/knowledge-base/pdfa/zugferd-invoices/>`_ which is based on CII.

Here is how the module works:

* the user starts a wizard and uploads the PDF invoice,
* if the PDF file has an embedded XML file, Odoo will read this file,
* otherwise, Odoo will use the *invoice2data* Python lib to try to interpret the text of the PDF,
* if there is already some draft supplier invoice for this supplier, propose to select one to update or create a new invoice
* create the draft supplier invoice and show it to the user, so that he can verify and then validate.

This module also works with supplier refunds.

Installation
============

This module requires the Python library *invoice2data* available on Github. The main project is `here <https://github.com/manuelRiel/invoice2data>`, but for the moment you should get Akretion's version available `here <https://github.com/akretion/invoice2data/tree/odoo-pdf-import>`.

To install the right version of the library, run:

```
sudo pip install git+https://github.com/akretion/invoice2data.git@odoo-pdf-import
```

Configuration
=============

To configure this module, go to the menu *Accounting > Configuration > Miscellaneous > Import Supplier Invoices* and create the import configuration entries for some suppliers.

Usage
=====

To use this module, go to the menu *Accounting > Suppliers > Import PDF Invoices* and select the PDF invoices of your supplier.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

 * Add support for more suppliers via a lib.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20account_invoice_pdf_import%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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
