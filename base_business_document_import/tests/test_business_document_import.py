# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestFrIntrastatService(TransactionCase):

    def test_match_partner(self):
        partner1 = self.env['res.partner'].create({
            'name': 'Total SA',
            'supplier': False,
            'customer': False,
            'ref': 'TOTAL',
            'website': 'www.total.com',
            })
        bdio = self.env['business.document.import']
        partner_dict = {'email': u' Agrolait@yourcompany.example.com'}
        res = bdio._match_partner(
            partner_dict, [], partner_type='customer')
        self.assertEquals(res, self.env.ref('base.res_partner_2'))
        # match on domain extracted from email with warning
        partner_dict = {'email': u'alexis.delattre@total.com'}
        warn = []
        res = bdio._match_partner(partner_dict, warn, partner_type=False)
        self.assertEquals(res, partner1)
        self.assertTrue(warn)
        partner_dict = {'name': u'delta pc '}
        res = bdio._match_partner(
            partner_dict, [], partner_type='supplier')
        self.assertEquals(res, self.env.ref('base.res_partner_4'))
        partner_dict = {'ref': u'TOTAL'}
        res = bdio._match_partner(partner_dict, [], partner_type=False)
        self.assertEquals(res, partner1)

    def test_match_shipping_partner(self):
        rpo = self.env['res.partner']
        bdio = self.env['business.document.import']
        partner1 = rpo.create({
            'name': 'Akretion France',
            'street': u'35B rue Montgolfier',
            'zip': '69100',
            'country_id': self.env.ref('base.fr').id,
            'email': 'contact@akretion.com',
            })
        cpartner1 = rpo.create({
            'parent_id': partner1.id,
            'name': u'Alexis de Lattre',
            'email': 'alexis.delattre@akretion.com',
            'use_parent_address': True,
            'type': 'delivery',
            })
        rpo.create({
            'parent_id': partner1.id,
            'name': u'Sébastien BEAU',
            'email': 'sebastien.beau@akretion.com',
            'use_parent_address': True,
            'type': 'default',
            })
        cpartner3 = rpo.create({
            'parent_id': partner1.id,
            'name': 'Flo',
            'email': 'flo@akretion.com',
            'street': "42 rue des lilas d'Espagne",
            'zip': '92400',
            'city': u'Courbevoie',
            'country_id': self.env.ref('base.fr').id,
            'type': 'invoice',
            })
        agrolait = self.env.ref('base.res_partner_2')
        shipping_dict = {
            'partner': {'email': 'contact@akretion.com'},
            'address': {},
            }
        res = bdio._match_shipping_partner(shipping_dict, agrolait, [])
        self.assertEquals(res, cpartner1)
        shipping_dict['address'] = {
            'zip': '92400',
            'country_code': 'fr',
            }
        res = bdio._match_shipping_partner(shipping_dict, agrolait, [])
        self.assertEquals(res, cpartner3)
        shipping_dict['address']['zip'] = '92500'
        res = bdio._match_shipping_partner(shipping_dict, agrolait, [])
        self.assertEquals(res, partner1)
        shipping_dict = {
            'partner': {},
            'address': {},
            }
        res = bdio._match_shipping_partner(shipping_dict, partner1, [])
        self.assertEquals(res, cpartner1)

    def test_match_currency(self):
        bdio = self.env['business.document.import']
        currency_dict = {'iso': u'EUR'}
        res = bdio._match_currency(currency_dict, [])
        self.assertEquals(res, self.env.ref('base.EUR'))
        currency_dict = {'symbol': u'€'}
        res = bdio._match_currency(currency_dict, [])
        self.assertEquals(res, self.env.ref('base.EUR'))
        currency_dict = {'country_code': u'fr '}
        res = bdio._match_currency(currency_dict, [])
        self.assertEquals(res, self.env.ref('base.EUR'))
        currency_dict = {'iso_or_symbol': u'€'}
        res = bdio._match_currency(currency_dict, [])
        self.assertEquals(res, self.env.ref('base.EUR'))
        self.env.user.company_id.currency_id = self.env.ref('base.KRW')
        currency_dict = {}
        res = bdio._match_currency(currency_dict, [])
        self.assertEquals(res, self.env.ref('base.KRW'))

    def test_match_product(self):
        bdio = self.env['business.document.import']
        ppo = self.env['product.product']
        product1 = ppo.create({
            'name': u'Test Product',
            'ean13': '9782203121102',
            'seller_ids': [
                (0, 0, {
                    'name': self.env.ref('base.res_partner_2').id,
                    'product_code': 'TEST1242',
                }),
                ]
            })
        product_dict = {'code': u'A2324 '}
        res = bdio._match_product(product_dict, [])
        self.assertEquals(res, self.env.ref('product.product_product_4b'))
        product_dict = {'ean13': u'9782203121102'}
        res = bdio._match_product(product_dict, [])
        self.assertEquals(res, product1)
        product_dict = {'code': 'TEST1242'}
        res = bdio._match_product(
            product_dict, [], seller=self.env.ref('base.res_partner_2'))
        self.assertEquals(res, product1)
        raise_test = True
        try:
            bdio._match_product(product_dict, [], seller=False)
            raise_test = False
        except:
            pass
        self.assertTrue(raise_test)

    def test_match_uom(self):
        bdio = self.env['business.document.import']
        uom_dict = {'unece_code': 'KGM'}
        res = bdio._match_uom(uom_dict, [])
        self.assertEquals(res, self.env.ref('product.product_uom_kgm'))
        uom_dict = {'unece_code': 'NIU'}
        res = bdio._match_uom(uom_dict, [])
        self.assertEquals(res, self.env.ref('product.product_uom_unit'))
        uom_dict = {'name': 'day'}
        res = bdio._match_uom(uom_dict, [])
        self.assertEquals(res, self.env.ref('product.product_uom_day'))
        uom_dict = {'name': ' Liter '}
        res = bdio._match_uom(uom_dict, [])
        self.assertEquals(res, self.env.ref('product.product_uom_litre'))
        uom_dict = {}
        product = self.env.ref('product.product_product_1')
        res = bdio._match_uom(uom_dict, [], product=product)
        self.assertEquals(res, product.uom_id)

    def test_match_tax(self):
        # on purpose, I use a rate that doesn't exist
        # so that this test works even if the l10n_de is installed
        de_tax_21 = self.env['account.tax'].create({
            'name': u'German VAT purchase 18.0%',
            'description': 'DE-VAT-buy-18.0',
            'type_tax_use': 'purchase',
            'price_include': False,
            'amount': 0.18,
            'type': 'percent',
            'unece_type_id': self.env.ref('account_tax_unece.tax_type_vat').id,
            'unece_categ_id': self.env.ref('account_tax_unece.tax_categ_s').id,
            })
        de_tax_21_ttc = self.env['account.tax'].create({
            'name': u'German VAT purchase 18.0% TTC',
            'description': 'DE-VAT-buy-18.0-TTC',
            'type_tax_use': 'purchase',
            'price_include': True,
            'amount': 0.18,
            'type': 'percent',
            'unece_type_id': self.env.ref('account_tax_unece.tax_type_vat').id,
            'unece_categ_id': self.env.ref('account_tax_unece.tax_categ_s').id,
            })
        bdio = self.env['business.document.import']
        tax_dict = {
            'type': 'percent',
            'amount': 18,
            'unece_type_code': 'VAT',
            'unece_categ_code': 'S',
            }
        res = bdio._match_tax(tax_dict, [], type_tax_use='purchase')
        self.assertEquals(res, de_tax_21)
        tax_dict.pop('unece_categ_code')
        res = bdio._match_tax(tax_dict, [], type_tax_use='purchase')
        self.assertEquals(res, de_tax_21)
        res = bdio._match_tax(
            tax_dict, [], type_tax_use='purchase', price_include=True)
        self.assertEquals(res, de_tax_21_ttc)
        res = bdio._match_taxes([tax_dict], [], type_tax_use='purchase')
        self.assertEquals(res, de_tax_21)
