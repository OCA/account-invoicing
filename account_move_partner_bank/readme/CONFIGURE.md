To set up a bank account for a partner:

- Go to the partner record.
- Under the Invoicing/Accounting tab, set the Recipient Bank field.
  If the partner has a company set, you can only select a bank account
  linked to that company’s partner. If the partner has no company set,
  you can only select a bank account linked to the current company’s
  partner. This is a company-dependent field.
  The field can be set on a child contact as well, so that a contact can be
  invoiced with a bank account of its own (e.g. a branch that collects on a
  different account than its head office). Whether the bank account of the parent
  company applies to its child contacts depends on the bank account sources
  configured below.

To use bank accounts in invoices:

- Go to Settings → Companies.
- Open a company record.
- In the Bank Account Sources tab, create one or more records.
  - Source Model: Select the model from which the bank field path is resolved
    (e.g., Account Move).
  - Bank Field Path: Enter the dot-path from the source model
    to a bank account (res.partner.bank), for example
    partner_id.bank_account_id or commercial_partner_id.bank_account_id.
    Every field of the path but the last one must be a many2one field.

The bank account from the record with the highest priority (lowest sequence number) will be used first
when assigning the bank on invoices. If no value is found, the system proceeds to the next record, and so on.

Sources can therefore be combined to let the bank account of a company apply to the
invoices of its child contacts, while a contact that has its own bank account still
takes precedence. To do so, configure the following two sources on Account Move:

- partner_id.bank_account_id, with the lower sequence number.
- commercial_partner_id.bank_account_id, with the higher sequence number.
