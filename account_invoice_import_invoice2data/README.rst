.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
Account Invoice Import Invoice2data
===================================

This module is an extension of the module *account_invoice_import*: it adds support for regular PDF invoices i.e. PDF invoice that don't have an embedded XML file. It uses the `invoice2data library <https://github.com/m3nu/invoice2data>`_ which takes care of extracting the text of the PDF invoice, find an existing invoice template and execute the invoice template to extract the useful information from the invoice.

To know the full story behind the development of this module, read this `blog post <http://www.akretion.com/blog/akretions-christmas-present-for-the-odoo-community>`_.

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

  sudo apt-get install imagemagick tesseract-ocr

If you want to use custom invoice templates for the invoice2data lib (instead of the templates provided by the invoice2data lib), you should add a line in your Odoo server configuration file such as:

.. code::

  invoice2data_templates_dir = /opt/invoice2data_local_templates

and store your invoice templates in YAML format (*.yml* extension) in the directory that you have configured above. If you add invoice tempates in this directory, you don't have to restart Odoo, they will be used automatically on the next invoice import.

French users should also install the module *l10n_fr_invoice_import* available in the `French localization <https://github.com/OCA/l10n-france/>`_, cf `this PR <https://github.com/OCA/l10n-france/pull/55>`_.

Configuration
=============

Go to the form view of the supplier and configure it with the following parameters:

* *is a Company ?* is True
* *Supplier* is True
* the *TIN* (i.e. VAT number) is set (the VAT number is used by default when searching the supplier in the Odoo partner database)
* in the *Accounting* tab, create an *Invoice Import Configuration*.

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
