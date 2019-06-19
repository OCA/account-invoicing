# © 2019 Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# © 2012-2015 SYLEAM Info Services (<http://www.syleam.fr/>)
# © 2015 Akretion (http://www.akretion.com)
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# @author: Sébastien LANGE <sebastien.lange@syleam.fr>
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Group Invoice Lines',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Add option to group invoice lines per account',
    'author': 'SYLEAM,Akretion,Dinamiche Aziendali srl,'
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/account-invoicing',
    'depends': ['account'],
    'data': ['views/account_journal.xml'],
    'installable': True,
}
