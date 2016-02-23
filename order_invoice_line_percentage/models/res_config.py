# -*- coding: utf-8 -*-
from openerp import models, fields, api


class account_config_settings(models.TransientModel):
    _inherit = 'account.config.settings'

    property_account_deposit_customer = fields.Many2one(
        'account.account',
        string='Account Advance Customer',
        domain=[('type', '!=', 'view')],
    )

    @api.multi
    def set_default_account_advance(self):
        """ set property advance account for customer and supplier """
        wizard = self[0]
        property_obj = self.env['ir.property']
        field_obj = self.env['ir.model.fields']
        todo_list = [
            ('property_account_deposit_customer',
             'res.partner', 'account.account'),
        ]
        for record in todo_list:
            account = getattr(wizard, record[0])
            value = account and 'account.account,' + str(account.id) or False
            if value:
                fields = field_obj.search(
                    [('name', '=', record[0]),
                     ('model', '=', record[1]),
                     ('relation', '=', record[2])])
                vals = {
                    'name': record[0],
                    'company_id': False,
                    'fields_id': fields and fields[0].id,
                    'value': value,
                }
                properties = property_obj.search([('name', '=', record[0])])
                if properties:
                    # the property exist: modify it
                    properties.write(vals)
                else:
                    # create the property
                    property_obj.create(vals)
        return True

    def get_default_account_advance(self, cr, uid, fields, context=None):
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        todo_list = [
            ('property_account_deposit_customer', 'res.partner'),
        ]
        res = {}
        for record in todo_list:
            prop = ir_property_obj.get(cr, uid,
                                       record[0], record[1], context=context)
            prop_id = prop and prop.id or False
            account_id = fiscal_obj.map_account(cr, uid, False, prop_id)
            res.update({record[0]: account_id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
