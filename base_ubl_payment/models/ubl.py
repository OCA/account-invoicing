# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.exceptions import Warning as UserError
from lxml import etree
import logging

logger = logging.getLogger(__name__)


class BaseUbl(models.AbstractModel):
    _inherit = 'base.ubl'

    @api.model
    def _ubl_add_payment_means(
            self, partner_bank, payment_mode, date_due, parent_node, ns,
            version='2.1'):
        pay_means = etree.SubElement(parent_node, ns['cac'] + 'PaymentMeans')
        pay_means_code = etree.SubElement(
            pay_means, ns['cbc'] + 'PaymentMeansCode', listID="UN/ECE 4461")
        # Why not schemeAgencyID='6' + schemeID
        if payment_mode:  # type is a required field on payment_mode
            if not payment_mode.type.unece_id:
                raise UserError(_(
                    "Missing 'UNECE Payment Mean' on payment type '%s' "
                    "used by the payment mode '%s'.") % (
                    payment_mode.type.name, payment_mode.name))
            pay_means_code.text = payment_mode.type.unece_code
        else:
            pay_means_code.text = '31'
            logger.warning(
                'Missing payment mode on invoice ID %d. '
                'Using 31 (wire transfer) as UNECE code as fallback '
                'for payment mean', self.id)
        if date_due:
            pay_due_date = etree.SubElement(
                pay_means, ns['cbc'] + 'PaymentDueDate')
            pay_due_date.text = date_due
        if pay_means_code.text in ['31', '42']:
            if not partner_bank and payment_mode:
                partner_bank = payment_mode.bank_id
            if partner_bank and partner_bank.state == 'iban':
                payee_fin_account = etree.SubElement(
                    pay_means, ns['cac'] + 'PayeeFinancialAccount')
                payee_fin_account_id = etree.SubElement(
                    payee_fin_account, ns['cbc'] + 'ID', schemeName='IBAN')
                payee_fin_account_id.text =\
                    partner_bank.acc_number.replace(' ', '')
                if partner_bank.bank_bic:
                    financial_inst_branch = etree.SubElement(
                        payee_fin_account,
                        ns['cac'] + 'FinancialInstitutionBranch')
                    financial_inst = etree.SubElement(
                        financial_inst_branch,
                        ns['cac'] + 'FinancialInstitution')
                    financial_inst_id = etree.SubElement(
                        financial_inst, ns['cbc'] + 'ID', schemeName='BIC')
                    financial_inst_id.text = partner_bank.bank_bic
