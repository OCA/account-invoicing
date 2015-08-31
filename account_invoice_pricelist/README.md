.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Pricelist on Invoices
=====================

* Add a stored field pricelist on invoices, related to the partner pricelist;
* Possibility to group by pricelist on account.invoice view;

.. image:: static/src/description/screenshot_group_by.png


This module doesn't add real feature by it self for end-users, but is usefull
to do reporting, in a inherited module.

Installation
============

Classical installation.

Configuration
=============

Nothing to do.

Note
====

* The field will not be stored for purchase invoices as long as 'purchase'
  module is not installed; (in invoice / in refund). (because purchase
  pricelist field on partner model is defined in 'purchase' module).

Usage
=====

To use this module, you need to:

* go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/account-invoicing/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* The pricelist field is readonly, so it's not possible to change it and to
  manage price changes;

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-invoicing/issues/new?body=module:%20account_invoice_pricelist%0Aversion:%208.0.1.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
