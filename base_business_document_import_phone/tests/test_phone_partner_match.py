# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestPhonePartnerMatch(TransactionCase):

    def test_phone_partner_match(self):
        rpo = self.env['res.partner']
        bdoo = self.env['business.document.import']
        partner = rpo.create({
            'name': u'Alexis de Lattre',
            'country_id': self.env.ref('base.fr').id,
            'supplier': True,
            'phone': '+33141981242',
            'fax': '+33141981243',
            })
        partner_dict = {
            'country_code': 'FR',
            'phone': '01.41.98.12.42',
            }
        res = bdoo._match_partner(partner_dict, [], partner_type='supplier')
        self.assertEquals(res, partner)
        partner_dict = {
            'country_code': 'FR',
            'fax': '(0)1-41-98-12-43',
            }
        res = bdoo._match_partner(partner_dict, [], partner_type='supplier')
        self.assertEquals(res, partner)
