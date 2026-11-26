# Dashboard Kanban View – Pending Items Roadmap

1. Drag & Drop Functionality

  - Goal: Override the JS so that when files are uploaded a `receipt` is created instead of a vendor bill.
  - Reference: [bill_guide.js – line 29](https://github.com/odoo/odoo/blob/d26148acaee5b5c995155780ec3993c5ae7210e6/addons/account/static/src/components/bill_guide/bill_guide.js#L29)

2. "Try our Sample" Button

  - Goal: Adapt the method to generate an editable `receipt` instead of a vendor bill.
  - Reference: [account_journal_dashboard.py – line 922](https://github.com/odoo/odoo/blob/d26148acaee5b5c995155780ec3993c5ae7210e6/addons/account/models/account_journal_dashboard.py#L922)
