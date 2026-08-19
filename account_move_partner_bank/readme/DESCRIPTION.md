This module adds a bank account field to partners and sets it
as the Recipient Bank on account moves based on the configuration of the
invoice's company.

The bank source configuration supports multiple source models, allowing the
same logic to be reused for other models (e.g., sale.order) by calling
`bank_account_source_ids.get_bank_for_record(record)`.

Note: If you want to add a bank account field to other models related to account
moves, you can extend the `bank.account.mixin` in a new module and simply add
the bank account field to the views.
