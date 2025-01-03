Odoo computes the currency rate applied on invoices, as well as for journal
items. However, these rates are simply computed based on the currency rates
that are configured in the system.

This module ensures that for posted entries the currency rates are computed
taking into account the actual amounts in the specific currency. This ensures
that the correct rates are displayed when an invoice was posted with a different
rate configuration, or if the user manually changed the amount in currency.
