# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Invoice Import module for Odoo
#    Copyright (C) 2015-2016 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Account Invoice Import',
    'version': '8.0.0.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Import supplier invoices/refunds as PDF or XML files',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['account', 'base_iban', 'base_vat_sanitized'],
    'external_dependencies': {'python': ['invoice2data', 'lxml']},
    'data': [
        'security/ir.model.access.csv',
        'account_invoice_import_config_view.xml',
        'wizard/account_invoice_import_view.xml',
        'partner_view.xml',
    ],
    'demo': ['demo/demo_data.xml'],
    'images': ['images/sshot-wizard1.png'],
    'installable': True,
}
