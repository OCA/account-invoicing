# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice Kanban',
    'summary': 'Add Kanban view in Invoice to follow administrative tasks',
    'version': '8.0.1.0.0',
    'website': 'https://www.elico-corp.com/',
    'author': 'Elico Corp, Odoo Community Association ()',
    'depends': [
        'account',
        'project',
    ],
    'data': [
        'demo/account_invoice_demo.xml',
        'views/account_invoice_view.xml',
        'views/project_task_kanban_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
