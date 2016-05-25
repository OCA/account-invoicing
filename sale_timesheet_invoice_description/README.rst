.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=========================
Timesheet details invoice
=========================

Add timesheet details in invoice line to invoices related with timesheets.


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
   :target: https://runbot.odoo-community.org/runbot/95/9.0

Known issues / Roadmap
======================

* Recovery states and others functional fields in Contracts.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Carlos Dauden <carlos.dauden@tecnativa.com>

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
