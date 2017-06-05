.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================================
Update Supplier Info of product from Supplier Invoice
=====================================================

This module allows to automatically update all products information in vendor bill for which the purchase information on the line are different from the supplier information defined in the product form.

It creates a new supplier information line if there is not any or it updates the first one in the list.

This module adds a new button 'Check Supplier Info' in supplier
invoice form.

.. image:: /account_invoice_supplierinfo_update/static/description/supplier_invoice_form.png


When the user clicks on it, he can see the supplier information changes that will apply. Optionally, he can remove some temporary changes, specially, if,
for example, a supplier applied an exceptional price change.

.. image:: /account_invoice_supplierinfo_update/static/description/main_screenshot.png

* blue: Creates a full new supplier info line
* brown: Updates current settings, displaying price variation (%)

This module adds an extra boolean field 'Supplier Informations Checked' in the
'Other Info' tab inside the supplier invoice form. 
This field indicates that the prices have been checked and
supplierinfo updated (or eventually that the changes have been ignored).

.. image:: /account_invoice_supplierinfo_update/static/description/supplier_invoice_form_other_info_tab.png

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Known Issues / Roadmap
======================

* This module does not manage correctly difference if

    * invoice line UoM are not the same as Supplierinfo UoM
    * invoice line taxes are not the same as products taxes. (If one is
      marked as tax included in the price and the other is marked as
      tax excluded in the price)

Credits
=======

Contributors
------------

* Chafique Delli <chafique.delli@akretion.com>
* Sylvain LE GAL (https://twitter.com/legalsylvain)
* Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>

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
