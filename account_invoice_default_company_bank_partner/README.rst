.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3


============================================
Account Invoice Default Company Bank Partner
============================================

This module adds default_company_bank_id to res.partner defined as many2one field with comodel_name=res.partner.bank.
The new field will be used to fill partner_bank_id on account.invoice by modifying onchange_partner_id method. It will be also add to res.partner form inside of tab 'Accounting'.

Installation
============

This module depends on:

* account

Configuration
=============

There is nothing to configure.

Known issues / Roadmap
======================

 * No known issues.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------
- Serpent Consulting Services Pvt. Ltd.
- Agile Business Group

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