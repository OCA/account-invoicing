# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestAccountInvoiceMassSending(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env['mass.send.print']
        cls.queue_obj = cls.env['queue.job']
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'type': 'service',
        })
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test account type',
        })
        cls.account = cls.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST_AIMS',
            'user_type_id': cls.account_type.id,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'account_id': cls.partner.property_account_receivable_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'account_id': cls.account.id,
                    'price_unit': 20,
                    'quantity': 1,
                    'uom_id': cls.product.uom_id.id,
                }),
            ]
        })
        cls.mail_template = cls.env['mail.template'].create({
            'name': 'Test mail template',
            'model_id': cls.env['account.invoice'],
        })

    def test_wizard_mass_send_print(self):
        wizard = self.wizard_obj.create({})
        wizard.template = self.mail_template
        wizard.with_context(
            active_ids=self.invoice.ids,
        ).wizard_mass_send_print()
        self.assertEqual(self.invoice.sending_in_progress, True)
        self.assertEqual(self.invoice.msp_mail_template, self.mail_template)
