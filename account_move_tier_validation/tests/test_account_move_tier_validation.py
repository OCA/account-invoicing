# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo.tests import SavepointCase


class TestAccountMoveTierValidation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user = cls.env.ref("base.user_demo")
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "user_validation_responsible_id": cls.user.id,
            }
        )

        cls.wizard = (
            cls.env["account.invoice.send.validation"]
            .with_context({"active_ids": cls.invoice.ids})
            .create({})
        )

    def test_wizard(self):
        """Check the wizard works."""
        self.assertEqual(self.wizard.composition_mode, "mass_mail")
        self.assertTrue(self.user.partner_id in self.wizard.partner_ids)
