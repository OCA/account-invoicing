.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl
    :alt: License: AGPL-3

================================
Account Invoice Send Mail Queued
================================

Send emails with invoices asynchronously when using the "Send & print" invoices action and multiple invoices have been selected.


Installation
============

The module queue_job is necessary to run 'account_invoice_send_mail_queued'. It can be found here:
https://github.com/OCA/queue


Configuration
=============

This module needs no special configuration. However, the module 'queue_job' needs some configuration: https://github.com/OCA/queue/blob/13.0/queue_job/README.rst


Usage
=====

To use this module, you need to:

#. Go to Invoicing
#. Select multiple invoices
#. Go to Action > "Send & print"
#. Check the "Email" option and click "Send"


ROADMAP
=======

* If a selected invoice to be asynchronously sent has been deleted when the action is executed, an error will occur.
* Invoices are sent asynchronously only if a template has been selected.


Bug Tracker
===========

Bugs and errors are managed in `issues of GitHub <https://github.com/OCA/account-invoicing/issues>`_.
In case of problems, please check if your problem has already been
reported. If you are the first to discover it, help us solving it by indicating
a detailed description `here <https://github.com/OCA/account-invoicing/issues/new>`_.

Do not contact contributors directly about support or help with technical issues.


Credits
=======

Authors
~~~~~~~

* Sygel


Contributors
~~~~~~~~~~~~

* Manuel Regidor <manuel.regidor@sygel.es>
* Valentín Vinagre <valentin.vinagre@sygel.es>


Maintainer
~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
