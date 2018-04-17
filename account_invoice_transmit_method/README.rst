.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
    :target: https://www.gnu.org/licenses/agpl
    :alt: License: AGPL-3

=======================
Invoice Transmit Method
=======================

This module allows to configure an *Invoice Transmit Method* on each partner. This module provides by default 3 transmission methods:

* E-mail
* Post
* Customer Portal

You can manually create additional transmission methods or other modules can create additional transmission methods (for example, the module *l10n_fr_chorus* creates a specific transmission method *Chorus*, which is the e-invoicing platform of the French administration).

Configuration
=============

If you need to add Transmit Methods, go to the menu *Invoicing > Configuration > Management > Transmit Methods*.

Usage
=====

On the form view of a parent Partner (not a Contact), in the *Accounting* tab, there are 2 fields:

* Customer Invoice Transmission Method
* Vendor Invoice Reception Method

When you create an invoice, this value is automatically copied on the invoice (and can be modified).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======
Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

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
