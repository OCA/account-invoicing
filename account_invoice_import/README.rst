.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Account Invoice Import
======================

This module has been started by lazy accounting users who hate enter they supplier invoices manually in Odoo. Almost all companies have several supplier invoices to enter regularly in the system from the same suppliers: phone bill, electricity bill, Internet access, train tickets, etc. Most of these invoices are available as PDF. We dream that we would be able to automatically extract from the PDF the required information to enter the invoice as supplier invoice in Odoo. To know the full story behind the development of this module, read this `blog post <http://www.akretion.com/blog/akretions-christmas-present-for-the-odoo-community>`_.

In the future, we believe we will have structured information embedded inside the metadata of PDF invoices. There are 2 main standards for electronic invoicing:

* `CII <http://tfig.unece.org/contents/cross-industry-invoice-cii.htm>`_ (Cross-Industry Invoice) developped by `UN/CEFACT <http://www.unece.org/cefact>`_ (United Nations Centre for Trade Facilitation and Electronic Business),
* `UBL <http://ubl.xml.org/>`_ (Universal Business Language) developped by `OASIS <https://www.oasis-open.org/>`_ (Organization for the Advancement of Structured Information Standards).

For example, there is already a standard in Germany called `ZUGFeRD <http://www.pdflib.com/knowledge-base/pdfa/zugferd-invoices/>`_ which is based on CII.

This module doesn't do anything useful by itself ; it requires other modules to work: each modules adds a specific invoice format.

Here is how the module works:

* the user starts a wizard and uploads the PDF or XML invoice,
* if it is an XML file, Odoo will parse it to create the invoice (requires additional modules for specific XML formats, such as the module *account_invoice_import_ubl* for the UBL format),
* if it is a PDF file with an embedded XML file in ZUGFeRD/CII format, Odoo will extract the embedded XML file and parse it to create the invoice (requires the module *account_invoice_import_zugferd*),
* otherwise, Odoo will use the *invoice2data* Python library to try to interpret the text of the PDF (requires the module *account_invoice_import_invoice2data*),
* if there is already some draft supplier invoice for this supplier, Odoo will propose to select one to update or create a new draft invoice,
* otherwise, Odoo will directly create a new draft supplier invoice and attach the PDF to it.

This module also works with supplier refunds.

Configuration
=============

Go to the form view of the suppliers and configure it with the following parameters:

* *is a Company ?* is True
* *Supplier* is True
* the *TIN* (i.e. VAT number) is set (the VAT number is used by default when searching the supplier in the Odoo partner database)
* in the *Accounting* tab, create an *Invoice Import Configuration*.

Usage
=====

To use this module, go to the menu *Accounting > Suppliers > Import Invoices* and upload a PDF or XML invoice of your supplier.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

Known issues / Roadmap
======================

* Remove dependency on *base_iban* and develop a separate glue module between this module and *base_iban*

* Enhance the update of an existing invoice by analysing the lines (lines are only available when the invoice has an embedded XML file)

* Add a mail gateway to be able to forward the emails that we receive with PDF invoices to a dedicated address ; the gateway would detach the PDF invoice from the email and create the draft supplier invoice in Odoo.

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
