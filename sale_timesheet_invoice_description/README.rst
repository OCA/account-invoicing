.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
Timesheet details invoice
=========================

Add timesheet details in invoice line to invoices related with timesheets.

Configuration
=============

To configure this module, you need to:

#. Go to *Sales -> Configuration -> Settings -> Quotations & Sales* and set
   Default Timesheet Invoice Description.


Usage
=====

To use this module, you need to:

#. Go to *Sales -> Sales Orders* and create a new Sales Orders.
#. Add line selecting a product with

   - *Invoicing Policy* -> **Delivered quantities**

   - *Track Service* -> **Timesheets on contract**

   e.g. *Support Contract (on timesheet)*
#. Confirm Sale
#. Go to *Timesheets -> Activities* and create line with same project of SO
#. Go to Sales Orders and select *Other Information* -> **Timesheet invoice
   description**
#. *Create Invoice*


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/11.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Carlos Dauden <carlos.dauden@tecnativa.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>


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
