.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

================================
 Account invoice merge auto pay
================================

This module completes the `account_invoice_merge_auto` module by
paying the customer invoices automatically once all invoice merge
candidates have been handled, have they finally been merged or not.

It uses the `queue_job_subscribe` module so that payments are performed
in their own database transaction: if one payment crashes for any
reason, the others are not affected and an administrator can be
notified (see Configuration below).


Usage
=====

First see `account_invoice_merge` and `account_invoice_merge_auto`
modules' usage.

Now create a customer invoice with a payment mode.


Configuration
=============

There is no configuration specific to this module, however following
parameters fit usually well together:

- Configure the `queue_job` module: define a user to be a job manager
  (in the `Configuration > Users` section) and to be notified in case
  of a failed job (`Configuration > Users > Connectors`)

- Also configure Odoo for `queue_job` of course: do not forget to add
  `queue_job` to the `server_wide_modules` option and to set `workers`
  to a suitable value (at least >= 1).

- Adjust the `Automatically merge invoices` cron task execution hour
  to your liking; for instance, if you use the `contract_auto_merge`
  module to generate the invoices to be merged and pay, disable the
  Contract automatic payment cron and set the Generate Recurring
  Invoices from Contracts cron to be executed before the
  `account_invoice_merge` one.
