.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Account invoice rounding
========================


Add a parameter to give a unit for rounding such as CHF 0.05 for Swiss
invoices


Installation
============

Just install it


Configuration
=============

To configure this module, you need to:

In Settings -> Configuration -> Accounting you will find 2 new types of
rounding

- `Swedish Round globally`

  To round your invoice total amount, this option will do the adjustment in
  the most important tax line of your invoice.

- `Swedish Round by adding an invoice line`

  To round your invoice total amount, this option create a invoice line without
  taxes on it. This invoice line is tagged as `is_rounding`

You can choose the account on which the invoice line will be written



Usage
=====


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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Nicola Malcontenti <nicola.malcontenti@agilebg.com>
* Akim Juillerat <akim.juillerat@camptocamp.com>

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
