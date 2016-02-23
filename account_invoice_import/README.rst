.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Account Invoice Import
======================

This module has been started by lazy accounting users who hate enter they supplier invoices manually in Odoo. As ERP consultants, we have several supplier invoices to enter regularly in the system from the same suppliers: phone bill, Internet access, train tickets, etc. Most of these invoices are available as PDF. We dream that we would be able to automatically extract from the PDF the required information to enter the invoice as supplier invoice in Odoo. To know the full story behind the development of this module, read this `blog post <http://www.akretion.com/blog/akretions-christmas-present-for-the-odoo-community>`_.

In the future, we believe we will have structured information embedded inside the metadata of PDF invoices. There are 2 main standards for electronic invoicing:

* `CII <http://tfig.unece.org/contents/cross-industry-invoice-cii.htm>`_ (Cross-Industry Invoice) developped by `UN/CEFACT <http://www.unece.org/cefact>`_ (United Nations Centre for Trade Facilitation and Electronic Business),
* `UBL <http://ubl.xml.org/>`_ (Universal Business Language) developped by `OASIS <https://www.oasis-open.org/>`_ (Organization for the Advancement of Structured Information Standards).

For example, there is already a standard in Germany called `ZUGFeRD <http://www.pdflib.com/knowledge-base/pdfa/zugferd-invoices/>`_ which is based on CII.

Here is how the module works:

* the user starts a wizard and uploads the PDF or XML invoice,
* if it is an XML file, Odoo will parse it to create the invoice,
* if it is a PDF file with an embedded XML file in ZUGFeRD/CII format, Odoo will extract the embedded XML file and parse it to create the invoice,
* otherwise, Odoo will use the *invoice2data* Python library to try to interpret the text of the PDF,
* if there is already some draft supplier invoice for this supplier, Odoo will propose to select one to update or create a new draft invoice,
* otherwise, Odoo will directly create a new draft supplier invoice and attach the PDF to it.

This module also works with supplier refunds.

Installation
============

This module requires the Python library *invoice2data* available on `Github <https://github.com/m3nu/invoice2data>`_.

To install the right version of the library, run:

.. code::

  sudo pip install git+https://github.com/m3nu/invoice2data.git

In order to use a recent version of invoice2data on Odoo v8, you need an Odoo v8 dated after January 29th 2016, so that it contains `this fix <https://github.com/odoo/odoo/commit/edeb5a8c0fb5c837364f1d92db731f89824bb28a>`_ which fixes `this bug <https://github.com/odoo/odoo/issues/10670>`_.

The invoice2data library requires the latest version of the *pdftotext* utility, which is not yet packaged in Debian/Ubuntu. So you should download it from `the FTP server of Foolabs <ftp://ftp.foolabs.com/pub/xpdf/xpdfbin-linux-3.04.tar.gz>`_ then uncompress it and copy the file *bin64/pdftotext* to */usr/local/bin*.

If you want the invoice2data library to fallback on OCR if the PDF doesn't contain text (only a very small minority of PDF invoices are image-based and require OCR), you should also install `Imagemagick <http://www.imagemagick.org/>`_ (to get the *convert* utility to convert PDF to TIFF) and `Tesseract OCR <https://github.com/tesseract-ocr/tesseract>`_ :

.. code::

  sudo add-get install imagemagick tesseract-ocr

French users should also install the module *l10n_fr_invoice_pdf_import* available in the `French localization <https://github.com/OCA/l10n-france/>`_.

Configuration
=============

To configure this module, go to the menu *Accounting > Configuration > Miscellaneous > Import Supplier Invoices* and create the import configuration entries for some suppliers.

Then, go to the form view of the suppliers and make sure that:

* *is a Company ?* is True
* *Supplier* is True
* the *TIN* (i.e. VAT number) is set (the VAT number is used by default when searching the supplier in the Odoo partner database)
* in the *Accounting* tab, select the *Invoice Import Configuration*.

For the PDF invoice of your supplier that don't have an embedded XML file, you will have to create a `template file <https://github.com/m3nu/invoice2data/blob/master/invoice2data/templates>`_ in YAML format in the invoice2data Python library. It is quite easy to do ; if you are familiar with `regexp <https://docs.python.org/2/library/re.html>`_, it should not take more than 10 minutes for each supplier.

Here are some hints to help you add a template for your supplier:

* Take `Free SAS template file <https://github.com/m3nu/invoice2data/blob/master/invoice2data/templates/fr/fr.free.adsl-fiber.yml>`_ as an example. You will find a sample PDF invoice for this supplier under invoice2data/test/pdfs/2015-07-02-invoice_free_fiber.pdf

* Try to run the invoice2data library manually on the sample invoice of Free:

.. code::

  % python -m invoice2data.main --debug invoice2data/test/pdfs/2015-07-02-invoice_free_fiber.pdf

On the output, you will get first the text of the PDF, then some debug info on the parsing of the invoice and the regexps, and, on the last line, you will have the dict that contain the result of the parsing.

* if the VAT number of the supplier is present in the text of the PDF invoice, I think it's a good idea to use it as the keyword. It is a good practice to add 2 other keywoards: one for the language (for example, match on the word *Invoice* in the language of the invoice) and one for the currency, so as to match only the invoices of that supplier in this particular language and currency.

* the list of *fields* should contain the following entries:

  * 'vat' with the VAT number of the supplier (if the VAT number of the supplier is not in the text of PDF file, add a 'partner_name' key, or, if the supplier is French and the module *l10n_fr_invoice_pdf_import* is installed, add a 'siren' key)
  * 'amount' ('amount' is the total amount with taxes)
  * 'amount_untaxed' or 'amount_tax' (one or the other, no need for both)
  * 'date': the date of the invoice
  * 'invoice_number'
  * 'date_due', if this information is available in the text of the PDF file.

Usage
=====

To use this module, go to the menu *Accounting > Suppliers > Import Invoices* and upload a PDF invoice of your supplier.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* Remove dependency on *base_iban* and develop a separate glue module between this module and *base_iban*

* Enhance the update of an existing invoice by analysing the lines (lines are only available when the invoice has an embedded XML file)

* Add a mail gateway to be able to forward the emails that we receive with PDF invoices to a dedicated address ; the gateway would detach the PDF invoice from the email and create the draft supplier invoice in Odoo.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20account_invoice_import%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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
