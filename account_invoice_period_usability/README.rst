.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===============================================================================
Display in the invoice supplier form the fiscal period next to the invoice date
===============================================================================

This module was written to improve the form of the supplier invoice (and refund) 
by displaying both the invoice date and the fiscal period fields side by side. 
It is more intuitive for the accountant to have a "single point of modification" 
for these two so-linked concepts.

The module does not affect client invoices for which the fiscal period has to 
follow the invoice date.

Tip: the module OCA/web/web_sheet_full_width can help to avoid fields wrapping 
and loose vertical space in the form.

Installation
============

There are no specific installation instructions for this module.

Configuration
=============

There are no specific configuration instructions for this module.

Usage
=====

On supplier invoice/refund form views, the period field is now 
right next to the date field.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/8.0

Known issues / Roadmap
======================

None.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20account_invoice_period_usability%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Olivier Laurent (<olivier.laurent@acsone.eu>)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.
