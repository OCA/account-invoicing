# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class WizardUpdateInvoiceSupplierinfo(models.TransientModel):
    _name = 'wizard.update.invoice.supplierinfo'

    line_ids = fields.One2many(
        comodel_name='wizard.update.invoice.supplierinfo.line',
        inverse_name='wizard_id', string='Lines')

    invoice_id = fields.Many2one(
        comodel_name='account.invoice', required=True, readonly=True,
        ondelete='cascade')

    state = fields.Selection(
        related='invoice_id.state', readonly=True)

    supplier_partner_id = fields.Many2one(
        comodel_name='res.partner', string='Supplier',
        related='invoice_id.supplier_partner_id', readonly=True)

    @api.multi
    def update_supplierinfo(self):
        self.ensure_one()
        supplierinfo_obj = self.env['product.supplierinfo']
        partnerinfo_obj = self.env['pricelist.partnerinfo']
        for line in self.line_ids:
            supplierinfo = line.supplierinfo_id
            partnerinfo = line.partnerinfo_id

            # Create supplierinfo if not exist
            if not supplierinfo:
                supplierinfo_vals = line._prepare_supplierinfo()
                supplierinfo = supplierinfo_obj.create(supplierinfo_vals)

            partnerinfo_vals = line._prepare_partnerinfo(supplierinfo)

            # Create partnerinfo if not exist
            if not line.partnerinfo_id:
                partnerinfo_obj.create(partnerinfo_vals)

            # Update partnerinfo, if exist
            else:
                partnerinfo.write(partnerinfo_vals)

        # Mark the invoice as checked
        self.invoice_id.write({'supplierinfo_ok': True})

    @api.multi
    def set_supplierinfo_ok(self):
        self.invoice_id.write({'supplierinfo_ok': True})

    @api.multi
    def update_supplierinfo_validate(self):
        self.update_supplierinfo()
        invoice = self.env['account.invoice'].browse(
            self._context['active_id'])
        invoice.signal_workflow('invoice_open')
