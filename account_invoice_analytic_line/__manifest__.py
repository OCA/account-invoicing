# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice analytic lines",
    "version": "10.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "",
    "summary": "Directly invoice analytic lines",
    "depends": [
        'account',
        'project',
        'hr_timesheet',
        'onchange_helper',
    ],
    "data": [
        "reports/account_invoice.xml",
        "wizards/account_config_settings.xml",
        "views/res_partner.xml",
        "views/project_project.xml",
        "wizards/account_invoice_analytic_line.xml",
        "views/account_invoice_analytic_line_discount.xml",
        "views/project_task.xml",
        "views/account_analytic_line.xml",
        "data/account_invoice_analytic_line_discount.xml",
        'security/ir.model.access.csv',
    ],
}
