Currently Odoo just provides a status for Draft/open/paid status which is not
enough to follow the full administrative process.

This administrative process can be sometimes quite complex with workflow that
might be different by customers.

Some are usual  steps:

* Timesheets created
* Timesheets report internal validation
* Timesheets Validated by the customer
* ERP invoice created
* ERP invoice validated
* Other documents (contracts, official invoice) printing
* Other documents (contracts, official invoice) delivery
* PR/PO or contract reception for payment (some customers)
* Payment received (=done)

This list may vary over time and from customers.

This module provides administrative stage management similar to the tasks in Odoo:

* Add a Stage in Invoice (like in tasks) with the separate field for the additional
  workflow on top of current one.
* No button to switch from stages: simply clicking on it is enough (like tasks)
* Add Kanban view, default with stage group by.
* Kanban becomes the default view.
