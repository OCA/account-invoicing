.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================
Unit rounded invoice (Cash Rounding) by currency
================================================

This module extends functionality of module `Unit rounded invoice <https://github.com/OCA/account-invoicing/tree/8.0/account_invoice_rounding>`_.

It allows to set, in accounting settings, a rounding precision for each currency,
such as 0.05 CHF for Swiss invoices.


Configuration
=============

#. in Settings > Configuration > Accounting, check Currencies Rounding Rules
#. Set currency rule for each currency you need to handle:

- `Swedish Round globally`

  To round your invoice total amount, this option will do the adjustment in
  the most important tax line of your invoice.

- `Swedish Round by adding an invoice line`

  To round your invoice total amount, this option will create a invoice line without
  taxes on it.
  This invoice line is tagged as `is_rounding`


Usage
=====

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
Alessio Gerace <alessio.gerace@agilebg.com>

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
