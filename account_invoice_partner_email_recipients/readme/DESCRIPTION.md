This module extends Odoo's invoice sending functionality to allow configuring multiple email recipients for customer invoices and credit notes.

By default in standard Odoo, invoices sent by email are only addressed to the single primary commercial partner unless extra recipients are manually selected every time the send wizard is opened. During batch sending or automated background sending, extra recipients cannot be specified.

With this module:
* Dedicated invoice email recipients can be configured per customer on the partner form.
* Invoices automatically inherit these recipients, with the option for accountants to add or remove recipients per invoice while in draft.
* When sending invoices (individually via the wizard, in batch, or via automated crons), all configured recipients are automatically included in the email distribution.
