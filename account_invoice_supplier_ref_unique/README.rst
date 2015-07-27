Unique Supplier Invoice Number
==============================

This module checks that a supplier invoice/refund is not entered twice. This is important because if you enter twice the same supplier invoice, there is also a risk that you pay it twice !

This module adds a constraint on supplier invoice/refunds to check that (commercial_partner_id, supplier_invoice_number) is unique, without considering the case of the supplier invoice number.

Credits
=======

Contributors
------------

* Marc Cassuto <marc.cassuto@savoirfairelinux.com>
* Mathieu Benoit <mathieu.benoit@savoirfairelinux.com>
* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
