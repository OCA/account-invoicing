.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Account Invoice View Payment
============================

This module allows users to access directly to the payment from an invoice
when registering a payment or afterwards.

The option to open the payment when it's being registered is useful
when the user needs to do a follow-up step on the payment, such as printing
the associated check.

Configuration
=============

Only users assigned to the group "Billing" can display the payments from
the invoice.

Usage
=====

Registering a payment
---------------------
#. Go to an open customer invoice or vendor bill and press 'Register Payment'.
#. Enter the payment details and press 'Validate & View Payment'.

After payment has been made
---------------------------
#. Go to an open customer invoice or vendor bill and press the link
   'View Payments' that appears next to the list of payments made for that
   invoice.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/96/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-payment/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------
* Jordi Ballester <jordi.ballester@eficent.com>
* Miquel Raïch <miquel.raich@eficent.com>
* Achraf Mhadhbi <machraf@bloopark.de>


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
