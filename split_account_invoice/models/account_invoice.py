# -*- coding: utf-8 -*-
from odoo import api,fields,models,_
from odoo.exceptions import ValidationError


class AccountInvoiceInherit(models.Model):
	_inherit = 'account.invoice'
	
	split_id = fields.Many2one(string="Split From",
	                           comodel_name='account.invoice',
	                           help="INV Splited From Ref:")
	
	def btn_split_quotation(self):
		"""
		Define function to split invoice when we click on button
		:return: New INV view
		"""
		for record in self:
			if record.invoice_line_ids:
				cnt = 0
				for rec in record.invoice_line_ids:
					if rec.split:
						cnt += 1
				if cnt >= 1:
					inv_id = record.copy()
					inv_id.write({
						'split_id': record.id
					})
					if inv_id:
						for line in inv_id.invoice_line_ids:
							if not line.split:
								line.unlink()
							else:
								line.split = False
					for invoice_line_ids in record.invoice_line_ids:
						if invoice_line_ids.split:
							self.env['account.invoice.line'].browse(invoice_line_ids.id).unlink()
					compose_tree = compose_form = False
					if record.type == 'in_invoice':
						compose_tree = self.env.ref('account.invoice_supplier_tree', False)
						compose_form = self.env.ref('account.invoice_supplier_form', False)
					elif record.type == 'out_invoice':
						compose_tree = self.env.ref('account.invoice_tree', False)
						compose_form = self.env.ref('account.invoice_form', False)
					return {
						'name': 'Splited Records',
						'type': 'ir.actions.act_window',
						'view_type': 'form',
						'view_mode': 'tree,form',
						'res_model': 'account.invoice',
						'views': [(compose_tree.id, 'tree'),(compose_form.id, 'form')],
						'view_id': compose_tree.id,
						'res.id': False,
						'target': 'current',
						'domain': [('id', 'in', [inv_id.id])],
						'context': {},
					}
				
				else:
					raise ValidationError(_('Please Select Line/Lines To Split'))
