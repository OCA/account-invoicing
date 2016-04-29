.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Force Invoice Number
====================

This module allows to force the invoice numbering.
It displays the internal_number field. If user fills that field, the typed
value will be used as invoice (and move) number.
Otherwise, the next sequence number will be retrieved and saved.
So, the new field has to be used when user doesn't want to use the default
invoice numbering for a specific invoice.

Usage
=====

Once installed, you'll find the Force Number field on all the invoices in draft
state in the Other Info tab.
You can then fill in this field with the invoice number you want to assign.
The invoice will get this number when confirmed.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/9.0

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

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Alex Comba <alex.comba@agilebg.com>
* Davide Corio <davide.corio@abstract.it>
* Francesco Apruzzese f.apruzzese@apuliasoftware.it>

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