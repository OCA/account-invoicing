# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Account Invoice Merge',
    'version': '11.0.1.0.0',
    'category': 'Finance',
    'summary': "Merge invoices in draft",
    'author': "Elico Corp,Odoo Community Association (OCA)",
    'website': 'http://www.openerp.net.cn',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'wizard/invoice_merge_view.xml',
    ],
    'installable': True,
}
