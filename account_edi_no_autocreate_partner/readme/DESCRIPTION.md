This module modifies the invoice import process so that no longer partners are
auto-created when no matching is found.

Instead, imported invoices that cannot be linked to an existing partner
are automatically assigned to a dedicated fallback partner named
"Partner Not Found".

This prevents uncontrolled partner creation and allows users to manually
review and correct partner information before posting invoices.
