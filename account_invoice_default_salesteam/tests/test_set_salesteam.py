# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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
from __future__ import unicode_literals
from openerp.tests.common import TransactionCase


class test_invoice_salesteam(TransactionCase):
    """
    Test setting the account_invoice's salesteam
    """
    def _ref(self, xmlref):
        module, _, xmlid = xmlref.partition(".")
        return self.model_data_obj.get_object_reference(self.cr, self.uid,
                                                        module, xmlid)[1]

    def setUp(self):
        super(test_invoice_salesteam, self).setUp()
        self.invoice_obj = self.registry("account.invoice")
        self.model_data_obj = self.registry("ir.model.data")
        self.partner_obj = self.registry("res.partner")

        self.section_id = self._ref("crm.crm_case_section_1")
        self.partner_id = self.partner_obj.create(
            self.cr, self.uid,
            {"name": "Test Partner",
             "section_id": self.section_id})

    def test_onchange(self):
        res = self.invoice_obj.onchange_partner_id(
            self.cr, self.uid, [], type=None, partner_id=self.partner_id)

        self.assertEquals(res["value"]["section_id"], self.section_id)

    def test_create(self):
        ref = self._ref
        inv_id = self.invoice_obj.create(
            self.cr, self.uid,
            {"account_id": ref("account.a_recv"),
             "company_id": ref("base.main_company"),
             "currency_id": ref("base.EUR"),
             "invoice_line": [(0, 0, {
                 "account_id": ref("account.a_sale"),
                 "name": "[PCSC234] PC Assemble SC234",
                 "price_unit": 450.0,
                 "quantity": 1.0,
                 "product_id": ref("product.product_product_3"),
                 "uos_id": ref("product.product_uom_unit"),
             })],
             "journal_id": ref("account.bank_journal"),
             "partner_id": self.partner_id,
             "reference_type": "none",
             }
        )

        inv = self.invoice_obj.browse(self.cr, self.uid, inv_id)
        self.assertEquals(inv.section_id.id, self.section_id)
