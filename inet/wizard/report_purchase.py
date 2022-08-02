# -*- coding: utf-8 -*-


from odoo import models, fields, api
from xlwt import easyxf, Workbook, Formula
from datetime import datetime

import base64
import StringIO


class ReportPurchase(models.TransientModel):
    _name = 'report.purchase'

    sale_id = fields.Many2one('sale.order', 'N OP', required=True)
    company_id = fields.Many2one('res.company', 'Compañia',
                                 default=lambda self: self.env['res.company']._company_default_get('report.purchase'))

    @api.multi
    def purchase_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/report_purchase?model=report.purchase&field=name&id=%s&filename=reporte compras.xls' % self.id,
            'target': 'self'
        }

    @api.multi
    def get_filename(self):
        return 'reporte compras.xls'

    @api.multi
    def _get_content(self):
        invoice = self.env['account.invoice']
        for obj in self:
            style1 = easyxf('align: wrap on, horiz justified;''borders: left thin, right thin, top thin, bottom thin')
            style2 = easyxf('font: height 280, name Arial, bold on;''align: wrap on, vert centre, horiz center;''borders: left thin, right thin, top thin, bottom thin;')
            style3 = easyxf('align: wrap on, horiz justified;''borders: left thin, right thin, top thin, bottom thin', num_format_str='0.00')
            style4 = easyxf(num_format_str='0.00')
            style5 = easyxf('font: bold on, name Arial, height 180;''align: wrap on, horiz justified;''borders: left thin, right thin, top thin, bottom thin')


            today = datetime.now().strftime('%Y-%d-%d')

            wbk = Workbook()
            ws = wbk.add_sheet('Compras')
            ws.write(7, 1, 'Compania', style1)
            ws.write(7, 2, obj.company_id.name, style1)
            ws.write(8, 1, 'RUC', style1)
            ws.write(8, 2, obj.company_id.vat, style1)
            ws.write(9, 1, 'Fecha', style1)
            ws.write(9, 2, today, style1)
            ws.write_merge(1, 4, 3, 11, 'Reporte de Liquidacion de Gastos', style2)
            ws.write(12, 1, 'N de OP', style1)
            ws.write(12, 2, obj.sale_id.name, style1)
            ws.write(13, 1, 'Nombre de Proyecto', style1)
            ws.write_merge(13, 13, 2, 5, obj.sale_id.client_order_ref, style1)
            ws.write(16, 1, 'Item', style5)
            ws.write(16, 2, 'Proveedor', style5)
            ws.col(2).width = len('Proveedor') * 800
            ws.write(16, 3, 'Producto', style5)
            ws.col(3).width = len('Producto') * 1400
            ws.write(16, 4, 'Cantidad', style5)
            ws.col(4).width = len('Cantidad') * 550
            ws.write(16, 5, 'Precio Unit', style5)
            ws.write(16, 6, 'SubTotal', style5)
            ws.write(16, 7, 'Fecha', style5)
            ws.write(16, 8, 'N Fact/Boleta/RPH', style5)
            ws.col(8).width = len('N Fact/Boleta/RPH') * 250
            ws.write(16, 9, 'Codigo Fact/Bol/RPH', style5)
            ws.col(9).width = len('Codigo Fact/Bol/RPH') * 250
            ws.write(16, 10, 'Solicitante', style5)
            ws.col(10).width = len('SOlicitante') * 500
            ws.write(16, 11, 'Centro de Costo', style5)
            ws.col(11).width = len('Centro de Costo') * 250
            ws.write(16, 12, 'Forma de Pago', style5)
            ws.col(12).width = len('Forma de Pago') *1200

            domain = [('sale_id', '=', obj.sale_id.id),
                      ('company_id', '=', obj.company_id.id)]

            obj_invoice = invoice.search(domain)

            if obj_invoice.exists():
                invoice_ids = obj_invoice.mapped('id')
                total_estimated = 0.0
                for inv in obj_invoice:
                    total_estimated += inv.sale_id.cost_totals
                    company_currency = inv.company_id.currency_id
                    inv_currency = inv.currency_id
                    if company_currency != inv_currency:
                        currency = inv.currency_id.with_context(date=inv.date_invoice)
                        total_estimated += currency.compute(total_estimated, company_currency)
                if len(invoice_ids) == 1:
                    domain2 = [('invoice_id', '=', invoice_ids[0])]
                    line = self.env['account.invoice.line'].search(domain2)
                else:
                    domain2 = [('invoice_id', 'in', tuple(invoice_ids))]
                    line = self.env['account.invoice.line'].search(domain2)

                row = 17
                item = 1
                for obj_line in line:
                    notes = ''
                    currency_company = obj_line.company_id.currency_id
                    currency_invoice = obj_line.invoice_id.currency_id
                    subtotal = obj_line.price_subtotal
                    if currency_company != currency_invoice:
                        currency = obj_line.invoice_id.currency_id.with_context(date=obj_line.invoice_id.date_invoice)
                        subtotal = currency.compute(subtotal, currency_company)

                    user = self.env['purchase.order'].search([('name', '=', obj_line.invoice_id.origin)], limit=1)
                    if user.exists():
                        notes = user.notes
                    ws.write(row, 1, item, style1)
                    ws.write(row, 2, obj_line.invoice_id.partner_id.name, style1)
                    ws.write(row, 3, obj_line.product_id.name, style1)
                    ws.write(row, 4, obj_line.quantity, style1)
                    ws.write(row, 5, obj_line.price_unit, style1)
                    ws.write(row, 6, subtotal, style3)
                    ws.write(row, 7, obj_line.invoice_id.date_invoice, style1)
                    ws.write(row, 8, obj_line.invoice_id.supplier_invoice_number, style1)
                    ws.write(row, 9, obj_line.invoice_id.journal_id.name[0], style1)
                    ws.write(row, 10, obj_line.invoice_id.user_id.name, style1)
                    ws.write(row, 11, obj_line.analytics_id.name, style1)
                    ws.write(row, 12, notes, style1)
                    row += 1
                    item += 1

                ws.write(row + 2, 4, 'Costo Estimado Prg/Serv')
                ws.write(row + 2, 5, total_estimated, style4)
                ws.write(row + 3, 4, 'Costo Real de Pre/Serv')
                ws.write(row + 3, 5, Formula("SUM($G12:$G%d)" % row), style4)
                ws.write(row + 4, 4, 'Diferencial')
                ws.write(row + 4, 5, Formula("$F%d-$F%d" % (row + 3, row + 4)), style4)

        file_data = StringIO.StringIO()
        wbk.save(file_data)
        return file_data.getvalue()
