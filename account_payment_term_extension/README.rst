Account Payment Term Extension
==============================

This module was written to extend the functionality of payment terms to support rounding, months and weeks on payment term lines.

By default in Odoo, if you have a payment term of *30 days end of months* and you invoice on January 30, you will have a due date on March 31st. With this module, if you configure the payment term line with months = 1, days = 0 and days2 = -1, you will have a due date on February 28th.

Configuration
=============

To configure the Payment Terms and see the new options on the Payment Term Lines, go to the menu Accounting > Configuration > Miscellaneous > Payment Terms.

Credits
=======

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
