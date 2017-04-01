# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Account Invoice Template",
    'version': '0.1',
    'category': 'Generic Modules/Accounting',
    'description': """
Templates for Invoices

User can configure invoice templates, useful for recurring invoices.
The amount of each template line can be computed (through python code)
or kept as user input. If user input, when using the template, user has to fill
the amount of every input lines.
The invoice form allows lo load, through a wizard, the template to use and the
amounts to fill.


Contributors
------------
Jalal ZAHID <j.zahid@auriumtechnologies.com>  ( Mig to v10 )
Lorenzo Battistini <lorenzo.battistini@agilebg.com>
Leonardo Pistone <leonardo.pistone@camptocamp.com>
Franco Tampieri <franco@tampieri.info>
""",
    'author': 'Agile Business Group, Aurium Technologies',
    'website': 'http://www.agilebg.com ; http://www.auriumtechnologies.com',
    'license': 'AGPL-3',
    "depends": ['account_move_template'],
    "data": [
        'invoice_template.xml',
        'wizard/select_template.xml',
        'security/ir.model.access.csv',
        ],
    "active": False,
    "installable": True
}
