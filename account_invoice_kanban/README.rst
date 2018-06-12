.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Account Invoice Kanban
=======================

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

Configuration
=============
Stage are set up in the Settings Menu of Odoo application (after switching to
Developer Mode):

#. go to Settings > Technical > Kanban > Stages.
#. Create a new stage

Usage
=====
#. Go to Invoicing menu --> Customers --> Customer Invoices
#. Enjoy the new kanban view
#. Drag and drop the invoices from stage to stage
#. In the form view, click on any new stage to change it

Roadmap / Known Issues
======================

* Invoice stages and status are currently not synchronized: this is so since
  every organization might have different needs and stages. Nevertheless, they
  can be easily sync'ed (at least from status to Stages) via server actions.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-invoicing/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Eric Caudal <eric.caudal@elico-corp.com>
* Victor M. Martin <victor.martin@elico-corp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
