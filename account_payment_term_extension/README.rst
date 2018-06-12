.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Account Payment Term Extension
==============================

This module extends the functionality of payment terms to :

* support rounding, months and weeks on payment term lines
* allow to set more than one day of payment in payment terms
* if a payment term date is a holiday, it is postponed to a selected date
* allow to apply a chronological order on lines

  * for example, with a payment term which contains 2 lines
  * on standard, the due date of all lines is calculated from the invoice date
  * with this feature, the due date of the second line is calculated from the
    due date of the first line

Configuration
=============

To configure the Payment Terms and see the new options on the Payment Term
Lines, you need to:

#. Go to the menu Accounting > Configuration > Management > Payment Terms.

To use multiple payment days, define for each payment term line which payment
days apply, separated by spaces, commas or dashes.  To use holidays, insert the
holiday and the date payment terms will be postponed to.

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
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.
* https://openclipart.org/detail/198659/mono-template-invoice
* https://openclipart.org/detail/5571/calendar-icon-large

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Alexis de Lattre <alexis.delattre@akretion.com>
* Julien Coux <julien.coux@camptocamp.com>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Simone Rubino <simone.rubino@agilebg.com> (www.agilebg.com)

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
