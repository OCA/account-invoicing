
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Account Invoice Line Pricelist
==============================

By installing this module, on customer/sale invoice lines the unit price will
be calculated based on the Price List set for the Customer.

By default, in the standard Odoo, the method 'product_id_change' of model
'account.invoice.line' doesn't take in consideration the pricelist assigned
to a customer when calculating the unit price of customer/sale invoice.

For invoices created from sale orders, product prices are already based on
price lists. This is the standard behavior on Odoo. Only for the invoices
created manually, the pricelist is not take in consideration.
This module aims to fix this behavior.




Configuration
=============

No special configuration is needed.


Usage
=====

To use this module, you need to:

#. Set a price list for a Customer
#. Create a sale invoice for that Customer
#. On invoice lines, add some products (of which price is defined in price list)
#. Check whether the unit prices of the products are set accordingly to the price list

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

* Andrea Stirpe <a.stirpe@onestein.nl>
* Antonio Esposito <a.esposito@onestein.nl>


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
