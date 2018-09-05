##############################################################################
#
#    Copyright 2004-2010 Tiny SPRL (http://tiny.be).
#    Copyright 2010-2011 Elico Corp.
#    Copyright 2016 Acsone (https://www.acsone.eu/)
#    Copyright 2017 Eficent Business and IT Consulting Services S.L. (http://www.eficent.com)
#    2010-2018 OmniaSolutions (<http://www.omniasolutions.eu>).
#    OmniaSolutions, Open Source Management Solution
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
#
##############################################################################

{
    'name': 'Account Invoice Merge',
    'version': '10.0.1.0.1',
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
