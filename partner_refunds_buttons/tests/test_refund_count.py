from openerp.tests.common import TransactionCase


class TestRefundCount(TransactionCase):
    """Tests for the default values
    """

    def setUp(self):
        super(TestRefundCount, self).setUp()
        self.account_invoice = self.env["account.invoice"]
        self.res_partner = self.env["res.partner"]

    def test_refund_count(self):
        partner_id = self.ref("base.res_partner_2")
        account_id = self.ref("account.iva")
        partner = self.res_partner.browse(partner_id)
        partner.customer = True
        partner.supplier = True

        self.assertEqual(partner.supplier_refund_count, 0)
        self.assertEqual(partner.customer_refund_count, 0)

        self.account_invoice.create({'partner_id': partner.id,
                                     'type': 'out_refund',
                                     'account_id': account_id})

        self.assertEqual(partner.supplier_refund_count, 0)
        self.assertEqual(partner.customer_refund_count, 1)

        self.account_invoice.create({'partner_id': partner.id,
                                     'type': 'in_refund',
                                     'account_id': account_id})

        self.account_invoice.create({'partner_id': partner.id,
                                     'type': 'in_refund',
                                     'account_id': account_id})

        self.assertEqual(partner.supplier_refund_count, 2)
        self.assertEqual(partner.customer_refund_count, 1)
