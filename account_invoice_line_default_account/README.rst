Account Invoice Line default Account
====================================

When entering sales or purchase invoices directly, the user has to select an
account which will be used as a counterpart in the generated move lines. Each
supplier will mostly be linked to one account. For instance when ordering paper
from a supplier that deals in paper, the counterpart account will mostly be
something like 'office expenses'. The same principle has been applied for
customers. This module will add a default counterpart expense and income
account to a partner, comparable to the similiar field in product. When an
invoice is entered, withouth a product, the field from partner will be used as
default. Also when an account is entered on an invoice line (not automatically
selected for a product), the account will be automatically linked to the
partner as default expense or income account, unless explicitly disabled in the
partner record.

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be> (BCIM sprl)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

