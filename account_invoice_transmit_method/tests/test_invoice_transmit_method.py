# Copyright 2017-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author: Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceTransmitMethod(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.post_method = cls.env.ref("account_invoice_transmit_method.post")
        cls.partner = cls.env["res.partner"].create(
            {
                "is_company": True,
                "name": "Old School Company",
                "customer_invoice_transmit_method_id": cls.post_method.id,
            }
        )
        cls.sale_journal = cls.env["account.journal"].create(
            {"code": "XYZZZ", "name": "sale journal (test)", "type": "sale"}
        )

    def test_create_invoice(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "journal_id": self.sale_journal.id,
            }
        )
        self.assertEqual(invoice.transmit_method_id, self.post_method)
