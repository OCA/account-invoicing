.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================================================
Update Discount Supplier Info of product from Supplier Invoice
==============================================================

This module is a glue module installed if the following module are installed:
* account_invoice_supplierinfo_update (same repository)
* product_supplierinfo_discount (purchase-workflow repository)

It allows to update discount on supplierinfo, if the invoice line has a
different discount value.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/8.0

Bug Tracker
===========

Bugs are tracked on GitHub Issues. In case of trouble, please check there
if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Known Issues / Roadmap
======================

* Odoo account module displays discounts on invoice lines only if sale module
  is installed, that is bad design. To avoid useless dependencies, this
  module does not depend on sale module, and so, displays allways discount
  features, even if the user doesn't belong to the group 
  'sale.group_discount_per_so_line'.

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

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its  widespread use.

To contribute to this module, please visit https://odoo-community.org.
