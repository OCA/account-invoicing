# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.tests.common import SavepointCase


class TestBaseInvoicingMode(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
