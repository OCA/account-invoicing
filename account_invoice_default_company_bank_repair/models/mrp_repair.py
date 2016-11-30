# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from openerp.osv import osv
from openerp.tools.translate import _


class mrp_repair(osv.osv):
    _inherit = 'mrp.repair'

    def action_invoice_create(self, cr, uid, ids, group=False, context=None):
        """ Creates invoice(s) for repair order.
        @param group: It is set to true when group invoice is to be generated.
        @return: Invoice Ids.
        """
        res = {}
        invoices_group = {}
        inv_line_obj = self.pool.get('account.invoice.line')
        inv_obj = self.pool.get('account.invoice')
        repair_line_obj = self.pool.get('mrp.repair.line')
        repair_fee_obj = self.pool.get('mrp.repair.fee')
        for repair in self.browse(cr, uid, ids, context=context):
            rp = repair.partner_id
            rpi = repair.partner_invoice_id
            res[repair.id] = False
            if repair.state in ('draft', 'cancel') or repair.invoice_id:
                continue
            if not (rp.id and rpi.id):
                raise osv.except_osv(_('No partner!'), _(
                    'You have to select a Partner Invoice Address \
                    in the repair form!'))
            comment = repair.quotation_notes
            if (repair.invoice_method != 'none'):
                if group and rpi.id in invoices_group:
                    inv_id = invoices_group[rpi.id]
                    invoice = inv_obj.browse(cr, uid, inv_id)
                    invoice_vals = {
                        'name': invoice.name + ', ' + repair.name,
                        'origin': invoice.origin + ', ' + repair.name,
                        'comment': (comment and (invoice.comment and
                                    invoice.comment + "\n" +
                                    comment or comment)) or (
                                    invoice.comment and invoice.comment or ''),
                    }
                    inv_obj.write(cr, uid, [inv_id],
                                  invoice_vals, context=context)
                else:
                    if not rp.property_account_receivable:
                        raise osv.except_osv(_('Error!'), _(
                            'No account defined for /'
                            'partner "%s".') % rp.name)
                    account_id = rp.property_account_receivable.id
                    inv = {
                        'name': repair.name,
                        'origin': repair.name,
                        'type': 'out_invoice',
                        'account_id': account_id,
                        'partner_id': rpi.id or rp.id,
                        'partner_bank_id': (rpi.default_company_bank_id.id or
                                            rp.default_company_bank_id.id),
                        'currency_id': repair.pricelist_id.currency_id.id,
                        'comment': repair.quotation_notes,
                        'fiscal_position': rp.property_account_position.id
                    }
                    inv_id = inv_obj.create(cr, uid, inv)
                    invoices_group[repair.partner_invoice_id.id] = inv_id
                self.write(cr, uid, repair.id, {
                    'invoiced': True, 'invoice_id': inv_id})

                for operation in repair.operations:
                    if operation.to_invoice:
                        if group:
                            name = repair.name + '-' + operation.name
                        else:
                            name = operation.name
                        OP = operation.product_id
                        if OP.property_account_income:
                            account_id = OP.property_account_income.id
                        elif OP.categ_id.property_account_income_categ:
                            account_id = OP.categ_id. \
                                property_account_income_categ.id
                        else:
                            raise osv.except_osv(_('Error!'), _(
                                'No account defined for product "%s".')
                                % operation.product_id.name)

                        invoice_line_id = inv_line_obj.create(cr, uid, {
                            'invoice_id': inv_id,
                            'name': name,
                            'origin': repair.name,
                            'account_id': account_id,
                            'quantity': operation.product_uom_qty,
                            'invoice_line_tax_id':
                                [(6, 0, [x.id for x in operation.tax_id])],
                            'uos_id': operation.product_uom.id,
                            'price_unit': operation.price_unit,
                            'price_subtotal': (operation.product_uom_qty *
                                               operation.price_unit),
                            'product_id': (operation.product_id and
                                           operation.product_id.id or False)
                        })
                        repair_line_obj.write(cr, uid, [operation.id], {
                            'invoiced': True,
                            'invoice_line_id': invoice_line_id})
                for fee in repair.fees_lines:
                    if fee.to_invoice:
                        if group:
                            name = repair.name + '-' + fee.name
                        else:
                            name = fee.name
                        if not fee.product_id:
                            raise osv.except_osv(_('Warning!'), _(
                                'No product defined on Fees!'))

                        if fee.product_id.property_account_income:
                            account_id = fee.product_id.\
                                property_account_income.id
                        elif fee.product_id.categ_id.\
                                property_account_income_categ:
                            account_id = fee.product_id.categ_id.\
                                property_account_income_categ.id
                        else:
                            raise osv.except_osv(_('Error!'), _(
                                'No account defined for product "%s".')
                                % fee.product_id.name)

                        invoice_fee_id = inv_line_obj.create(cr, uid, {
                            'invoice_id': inv_id,
                            'name': name,
                            'origin': repair.name,
                            'account_id': account_id,
                            'quantity': fee.product_uom_qty,
                            'invoice_line_tax_id':
                                [(6, 0, [x.id for x in fee.tax_id])],
                            'uos_id': fee.product_uom.id,
                            'product_id': (fee.product_id and
                                           fee.product_id.id or False),
                            'price_unit': fee.price_unit,
                            'price_subtotal': (fee.product_uom_qty *
                                               fee.price_unit)
                            })
                        repair_fee_obj.write(cr, uid, [fee.id], {
                            'invoiced': True,
                            'invoice_line_id': invoice_fee_id})
                inv_obj.button_reset_taxes(cr, uid, inv_id, context=context)
                res[repair.id] = inv_id
        return res
