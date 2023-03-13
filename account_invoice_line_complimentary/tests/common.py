#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tests
from odoo.tests import Form


def create_complimentary_account(env):
    complimentary_account_form = Form(env['account.account'])
    complimentary_account_form.name = 'Test Complimentary Account'
    complimentary_account_form.code = 'TCA'
    complimentary_account_form.user_type_id = \
        env.ref('account.data_account_type_current_assets')
    complimentary_account = complimentary_account_form.save()
    return complimentary_account


def set_complimentary_account(env, complimentary_account):
    settings_form = Form(env['res.config.settings'])
    settings_form.complimentary_account_id = complimentary_account
    settings = settings_form.save()
    result = settings.execute()
    return result


def create_invoice(env, invoice_values, lines_values, tax):
    invoice_form = Form(
        env['account.invoice'],
        view='account.invoice_form',
    )
    for invoice_field, invoice_value in invoice_values.items():
        setattr(invoice_form, invoice_field, invoice_value)

    for line_values in lines_values:
        with invoice_form.invoice_line_ids.new() as line:
            for line_field, line_value in line_values.items():
                setattr(line, line_field, line_value)
            line.invoice_line_tax_ids.clear()
            line.invoice_line_tax_ids.add(tax)
    invoice = invoice_form.save()
    return invoice


class Common (tests.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': "Test Customer",
            'customer': True,
        })

        tax_22_form = Form(cls.env['account.tax'])
        tax_22_form.name = 'Test 22 Tax'
        tax_22_form.amount_type = 'percent'
        tax_22_form.amount = 22
        cls.tax_22 = tax_22_form.save()

        cls.complimentary_account = create_complimentary_account(cls.env)
