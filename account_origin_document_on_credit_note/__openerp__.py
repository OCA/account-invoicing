# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<www.savoirfairelinux.com>).
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
    'name': 'Origin Document on Credit Note',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
Origin Document on Credit Note
==============================

This module fills the field origin when creating a credit note from an invoice.

Contributors
------------
* Joao Alfredo Gama Batista (joao.gama@savoirfairelinux.com)
    """,
    'author': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'depends': [
        'account',
    ],
    'data': [],
    'installable': True,
    'auto_install': False,
}
