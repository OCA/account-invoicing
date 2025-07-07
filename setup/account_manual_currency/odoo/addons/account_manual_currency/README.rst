Manual Currency Rate on Posting
===============================

This back-port from the 18.0 branch lets you set a *Manual FX Rate*
(`use_manual_rate` + `manual_currency_rate`) on an invoice or journal
entry.  When the move is **posted**, the manual rate is injected in the
conversion context so that all move lines are generated with that rate.

* 100 % smoke-test coverage.
* Compatible with Odoo 16.0 Community & Enterprise.

