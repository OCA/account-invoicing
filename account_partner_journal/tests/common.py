from odoo.tests import common


class DefaultPurchaseJournalTest(common.TransactionCase):
    """Base class - Test the Default Purchase Journal in partner."""

    def setUp(self):
        super().setUp()
        # Useful models
        self.PurchaseOrder = self.env["purchase.order"]
        self.AccountInvoice = self.env["account.move"]
        self.AccountAccount = self.env["account.account"]
        self.supplier_id = self.env.ref("base.res_partner_3")
        self.product_id_1 = self.env.ref("product.product_product_8")

        self.purchase_journal = self.env["account.journal"].create(
            {
                "name": "Purchase Journal",
                "type": "purchase",
                "code": "PJT0",
            }
        )

        self.supplier_id.default_purchase_journal_id = self.purchase_journal.id
