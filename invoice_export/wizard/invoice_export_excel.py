import io
from datetime import datetime

import xlwt
from xlwt import easyxf

from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class InvoiceExcelExport(models.TransientModel):
    _name = 'invoice.excel.export'
    _description = 'Invoice Excel Export'
    
    invoice_ids = fields.Many2many('account.invoice', string='Invoice')
    file_data = fields.Binary('File Data')
    filename = fields.Char('Filename', default='Invoice Excel.xls')

    @api.multi
    def export_report_xlsx(self):
        import base64
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Invoices')
        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color blue; align: horiz center;font: color white; font:bold True;' "borders: top thin,left thin,right thin,bottom thin")
        text_left = easyxf('font:height 200; align: horiz left;' "borders: top thin,bottom thin")
        #text_center = easyxf('font:height 200; align: horiz center;' "borders: top thin,bottom thin")
        #text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin")
        worksheet.write(0, 0, 'Invoice ID', header_style)
        worksheet.write(0, 1, 'Sale Order ID', header_style)
        worksheet.write(0, 2, 'Date Of Sales Order', header_style)
        worksheet.write(0, 3, 'Pick Order ID', header_style)
        worksheet.write(0, 4, 'Date of Shipping', header_style)
        worksheet.write(0, 5, 'Name of Delivery Address', header_style)
        worksheet.write(0, 6, 'Full Delivery Address', header_style)
        worksheet.write(0, 7, 'Delivery email', header_style)
        worksheet.write(0, 8, 'Traking Ref', header_style)
#         worksheet.write(0, 9, 'Traking URL', header_style)
        i = 1
        for inv in self.invoice_ids:
            worksheet.write(i, 0, inv.number or '', text_left)
            if not inv.sale_order_ids:
                i += 1
            for order in inv.sale_order_ids:
                worksheet.write(i, 1, order.name or '', text_left)
                date_order = order.date_order.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                order_date = datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d.%m.%Y')
                worksheet.write(i, 2, order_date or '', text_left)
                if not order.picking_ids:
                    i += 1
                for pick in order.picking_ids:
                    worksheet.write(i, 3, pick.name or '', text_left)
                    date_pick = pick.date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    pick_date = datetime.strptime(date_pick, DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d.%m.%Y')
                    worksheet.write(i, 4, pick_date or '', text_left)
                    worksheet.write(i, 5, pick.partner_id.name or '', text_left)
                    delivery_address = ''
                    if pick.partner_id.street:
                        delivery_address += pick.partner_id.street + ','

                    if pick.partner_id.street2:
                        delivery_address += pick.partner_id.street2 + ','

                    if pick.partner_id.city:
                        delivery_address += pick.partner_id.city + ','

                    if pick.partner_id.zip:
                        delivery_address += pick.partner_id.zip + ','

                    if pick.partner_id.state_id:
                        delivery_address += pick.partner_id.state_id.name + ','

                    if pick.partner_id.country_id:
                        delivery_address += pick.partner_id.country_id.name + ','
                    delivery_address = delivery_address[:-1]
                    worksheet.write(i, 6, delivery_address or '', text_left)
                    if pick.partner_id.email:
                        worksheet.write(i, 7, pick.partner_id.email or '', text_left)
                    
                    worksheet.write(i, 8, pick.carrier_tracking_ref or '', text_left)
#                     if not pick.delivery_ids:
#                         i += 1
#                     for delivery in pick.delivery_ids:
#                         carrier = delivery.carrier_id
#                         worksheet.write(i, 8, delivery.carrier_tracking_ref or '', text_left)

#                         url = carrier and carrier.tracking_url_base or ''
#                         date_delivery = delivery.date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#                         d = datetime.strptime(date_delivery, DEFAULT_SERVER_DATETIME_FORMAT)
#                         url = url.replace('<TAG>', str(d.day)).replace('<MONAT>', str(d.month)).replace('<JAHR>', str(d.year))
#                         url = url.replace('<TRACKING-NUMMER>', delivery.carrier_tracking_ref)
#                         worksheet.write(i, 9, url or '', text_left)
                    i += 1
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        self.write({'file_data': base64.b64encode(data)})
        action = {
            'name': 'Invoice Excel',
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model=invoice.excel.export&id=" + str(self.id) + "&field=file_data&download=true&filename=invoice_excel.xls",
            'target': 'self',
            }
        return action
