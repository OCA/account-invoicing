This module avoids sending unnecessary invoice emails to internal users in two
specific situations.

First, when invoices are created, Odoo can notify internal users with an email
such as "You have been assigned to invoice NNNN". This module creates invoices
with `mail_auto_subscribe_no_notify=True` in the context, so those automatic
assignment/subscription emails are not sent to internal users.

Second, when an administration user sends an invoice email to the customer from
Odoo, internal users that follow the invoice, such as salespeople, do not need
to receive a copy of that customer-facing email. This module removes recipients
whose notification type is `user` from regular invoice comment notifications
(`mail.mt_comment`), while keeping customer recipients.

The module does not block internal chatter notifications. Internal notes and
other non-comment subtypes are left unchanged, so internal users can still be
notified when another user writes an internal note on the invoice.
