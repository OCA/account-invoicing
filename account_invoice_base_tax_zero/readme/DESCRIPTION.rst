This module, in case of invoice with amount zero, it generates account move
lines for tax and partner.

This module is needed to vat reports where is it important to see vat moves,
also when they are zero.

The module account_tax_balance, when a move is zero, sets always the account move type
as refund. So this module in case of invoice with amount zero, provides to set
the move type from invoice's type.
