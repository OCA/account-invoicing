.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Unique Supplier Invoice Number
==============================

This module checks that a supplier invoice/refund is not entered twice. This is important because if you enter twice the same supplier invoice, there is also a risk that you pay it twice !

This module adds a constraint on supplier invoice/refunds to check that (commercial_partner_id, supplier_invoice_number) is unique, without considering the case of the supplier invoice number.

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

* Marc Cassuto <marc.cassuto@savoirfairelinux.com>
* Mathieu Benoit <mathieu.benoit@savoirfairelinux.com>
* Alexis de Lattre <alexis.delattre@akretion.com>
* Thomas Binsfeld <thomas.binsfeld@acsone.eu>

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
