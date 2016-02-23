# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Invoice Import ZUGFeRD module for Odoo
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
    'name': 'Account Invoice Import ZUGFeRD',
    'version': '8.0.0.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Import ZUGFeRD-compliant supplier invoices/refunds',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['account_invoice_import', 'base_zugferd', 'base_vat'],
    'external_dependencies': {'python': ['pdfminer', 'lxml']},
    'data': [],
    'demo': ['demo/demo_data.xml'],
    'test': ['test/zugferd.yml'],
    'installable': True,
}
