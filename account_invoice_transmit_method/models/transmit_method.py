# Copyright 2017-2020 Akretion France (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TransmitMethod(models.Model):
    _name = "transmit.method"
    _description = "Transmit Method of a document"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        copy=False,
        help="Do not modify the code of an existing Transmit Method "
        "because it may be used to identify a particular transmit method.",
    )
    active = fields.Boolean("active", default=True)
    customer_ok = fields.Boolean(string="Selectable on Customers", default=True)
    supplier_ok = fields.Boolean(string="Selectable on Vendors", default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "This transmit method code already exists!")
    ]
