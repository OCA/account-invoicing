.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========================
Reimbursables management
========================

This module adds the option to add reimbursables to supplier invoices.

Reimbursables are payments for services that your supplier has made on behalf
of your company as part of an agreement.
Your company receives two invoices: one from the supplier, that includes
the reimbursable, and your company should pay, and one from the third party
that has been paid by your supplier on your behalf.

For example, when you set up a company your lawyer might pay for various
government fees on your behalf, that the lawyer is then going to pass on to you
as a reimbursable in the invoice. You will still receive an invoice for the
government fees, but you have no obligation to pay them, because they have
already been paid by your lawyer.

Usage
=====

#. Go to 'Accounting/Invoicing > Purchases > Documents > Vendors Bills'
#. Create an invoice for a provider and add the reimbursables on the
   reimbursable page
#. Validate the invoice

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/11.0

Known issues / Roadmap
======================

* Residual is wrong while the amount of the reimbursable is not assigned to the real supplier invoice.
  It is solved on https://github.com/odoo/odoo/pull/24915

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

* Enric Tobella <etobella@creublanca.es>

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
