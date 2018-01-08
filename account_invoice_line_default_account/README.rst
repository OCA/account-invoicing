.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
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

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/10.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/{project_repo}/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Ronald Portier, Therp
* Jacques-Etienne Baudoux <je@bcim.be> (BCIM sprl)

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
