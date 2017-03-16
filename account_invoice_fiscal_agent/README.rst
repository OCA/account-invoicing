.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Account Fiscal Agent
====================

This module automates accounting entries of fiscal agent companies.

Use case
--------

Company A is located in country A.
Company B is located in country B and is the fiscal agent of company A, for country B.
When company A issues an invoice to customer C (of country B), company B has to manage fiscal matters on behalf of Company A.

This module allows you to configure fiscal agent accounts, journals, and taxes in fiscal positions of company A. So that, upon validating the invoice of company A, a new invoice (for company B) is created in the name of same partner with the above pre-configured details.

Usage
=====

To use this module, you need to:

* Map fiscal agent accounts, journals and taxes in the Fiscal Position. This must be done by a user who can see data from both the companies

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

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Serpent Consulting Services Pvt. Ltd.
* Agile Business Group


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
