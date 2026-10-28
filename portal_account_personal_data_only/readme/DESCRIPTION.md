By default, portal users are allowed to see all the invoices of their
commercial partner. That could cause a leaking of documents between
members and departments of the organization that should stay private.

This module restricts that behavior so the portal users only see their
own documents: the invoices whose partner is the user's partner (or one
of its descendants), or the ones the user's partner (or one of its
descendants) is following.

A similar module named `portal_sale_personal_data_only` exists to do the
same for sale orders.
