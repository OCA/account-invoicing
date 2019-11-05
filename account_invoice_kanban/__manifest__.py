# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice Kanban',
    'summary': 'Add Kanban view in Invoice to follow administrative tasks',
    'version': '12.0.1.0.0',
    'website': 'https://github.com/OCA/account-invoicing',
    'author': 'initOS GmbH, Elico Corp, Odoo Community Association (OCA)',
    'depends': [
        'account',
        'base_kanban_stage',
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'demo': [
        'demo/account_invoice_demo.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
