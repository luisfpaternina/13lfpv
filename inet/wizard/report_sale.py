# -*- coding: utf-8 -*-


from odoo import models, fields, api
from xlwt import easyxf, Workbook, Formula
from datetime import datetime

import base64
#import StringIO
from io import StringIO
import pytz
import time


STATE = {
    'paid': 'Pagado'
}

class AccountPeriod(models.TransientModel):
    _name = 'account.period'
    _rec_name = 'name'

    name = fields.Char(string="Nombre")
    period_start = fields.Date(string="Inicio")
    period_end = fields.Date(string="Fin")


class ReportSale(models.TransientModel):
    _name = 'report.sale'

    period_start = fields.Many2one('account.period', 'Inicio', required=True)
    period_end = fields.Many2one('account.period', 'Fin', required=True)
    user_id = fields.Many2one('res.users', 'Comercial')
    currency_id = fields.Many2one('res.currency', 'Divisa')
    company_id = fields.Many2one('res.company', 'Compañia',
                                 default=lambda self: self.env['res.company']._company_default_get('report.sale'))

    def report_sale_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/report_sale?model=report.sale&field=name&id=%s&filename=reporte ventas.xls' % self.id,
            'target': 'self'
        }

    def get_filename(self):
        return 'reporte ventas.xls'

    def _get_content(self):
        account_invoice = self.env['account.invoice']
        order_line = self.env['account.invoice.line']
        sale_order = self.env['sale.order']
        for obj in self:
            style1 = easyxf('align: wrap on, horiz justified;''borders: left thin, right thin, top thin, bottom thin')
            style2 = easyxf('font: height 280, name Arial, bold on;''align: wrap on, vert centre, horiz center;''borders: left thin, right thin, top thin, bottom thin;')
            style3 = easyxf('align: wrap on, horiz justified;''borders: left thin, right thin, top thin, bottom thin', num_format_str='0.00')
            month_start = datetime.strptime(obj.period_start.date_start,
                                            '%Y-%m-%d').strftime('%B')
            month_end = datetime.strptime(obj.period_end.date_stop,
                                          '%Y-%m-%d').strftime('%B')

            now = datetime.now().strftime('%Y-%m-%d')

            wbk = Workbook()
            ws = wbk.add_sheet('Ventas')
            ws.write(9, 1, 'Compania', style1)
            ws.write(9, 2, obj.company_id.name, style1)
            ws.write(10, 1, 'RUC', style1)
            ws.write(10, 2, obj.company_id.vat, style1)
            ws.write(12, 1, 'Fecha', style1)
            ws.write(12, 2, now, style1)
            ws.write(13, 1, 'Periodo', style1)
            ws.write(13, 2, month_start, style1)
            ws.write(13, 3, 'A', style1)
            ws.write(13, 4, month_end, style1)
            ws.write_merge(1, 4, 3, 11, 'REPORTE DE VENTAS', style2)
            ws.write(16, 1, 'N Item', style1)
            ws.write(16, 2, 'Cliente', style1)
            ws.col(2).width = len('Cliente') * 1100
            ws.write(16, 3, 'Descripcion del producto', style1)
            ws.col(3).width = len('Descripcion del proucto') * 700
            ws.write(16, 4, 'Distribucion Analitica', style1)
            ws.col(4).width = len('Distribución Analitica') * 300
            ws.write(16, 5, 'Subtotal', style1)
            ws.col(5).width = len('Subtotal') * 500
            ws.write(16, 6, 'Total', style1)
            ws.write(16, 7, 'Costo', style1)
            ws.write(16, 8, 'Utilidad', style1)
            ws.write(16, 9, 'Comision comercial', style1)
            ws.write(16, 10, 'Comercial', style1)
            ws.col(10).width = len('Comercial') * 500
            ws.write(16, 11, 'Estado de Factura', style1)
            ws.col(11).width = len('Estado de Factura') * 300
            ws.write(16, 12, 'N Factura', style1)
            ws.write(16, 13, 'N OP', style1)
            ws.write(16, 14, 'Fecha de Emision', style1)
            ws.write(16, 15, 'Forma de Pago', style1)
            ws.write(16, 16, 'Fecha de Pago', style1)

            domain = [('date_invoice', '>=', obj.period_start.date_start),
                      ('date_invoice', '<=', obj.period_end.date_stop),
                      ('company_id', '=', obj.company_id.id),
                      ('type', '=', 'out_invoice'),
                      ('state', 'not in', ('draft', 'cancel'))]

            if obj.currency_id:
                domain.append(('currency_id', '=', obj.currency_id.id))

            if obj.user_id:
                domain.append(('user_id', '=', obj.user_id.id))

            obj_inv = account_invoice.search(domain)

            if obj_inv.exists():
                sale_ids = obj_inv.mapped('id')
                domain2 = [('invoice_id', 'in', tuple(sale_ids))]
                obj_line = order_line.search(domain2)
                row = 17
                item = 1
                for line in obj_line:
                    order_id = sale_order.search([('name', '=', line.invoice_id.origin)],
                                                 limit=1).id

                    domain3 = [('order_id', '=', order_id),
                               ('product_id', '=', line.product_id.id)]

                    estimated = self.env['estimated.sale'].search(domain3, limit=1)
                    cost = utility = commision = 0.0
                    if estimated.exists():
                        cost = estimated.cost_total
                        utility = estimated.amount_utility
                        commision = estimated.commision

                    subtotal = line.price_subtotal
                    total = subtotal * 1.18

                    if obj.currency_id.name == 'PEN' or not obj.currency_id:
                        date_cu = datetime.strptime(line.invoice_id.date_invoice,
                                                    '%Y-%m-%d').strftime('%Y-%m-%d')
                        currency = line.invoice_id.currency_id.with_context(date=date_cu)
                        subtotal = currency.compute(subtotal, line.company_id.currency_id)
                        total = currency.compute(total, line.company_id.currency_id)
                        cost = currency.compute(cost, line.company_id.currency_id)
                        utility = currency.compute(utility, line.company_id.currency_id)
                        commision = currency.compute(commision, line.company_id.currency_id)

                    state = STATE.get(line.invoice_id.state, 'Pendiente de Pago')

                    ws.write(row, 1, item, style1)
                    ws.write(row, 2, line.invoice_id.partner_id.name, style1)
                    ws.write(row, 3, line.product_id.name, style1)
                    ws.write(row, 4, line.analytics_id.name, style1)
                    ws.write(row, 5, subtotal, style3)
                    ws.write(row, 6, total, style3)
                    ws.write(row, 7, cost, style3)
                    ws.write(row, 8, utility, style3)
                    ws.write(row, 9, commision, style3)
                    ws.write(row, 10, line.invoice_id.user_id.name, style1)
                    ws.write(row, 11, state, style1)
                    ws.write(row, 12, line.invoice_id.voucher_number, style1)
                    ws.write(row, 13, line.invoice_id.origin, style1)
                    ws.write(row, 14, line.invoice_id.date_invoice, style1)
                    ws.write(row, 15, line.invoice_id.payment_term.name, style1)
                    ws.write(row, 16, line.invoice_id.date_due, style1)
                    row += 1
                    item += 1

                ws.write(row + 2, 5, 'Subtotal')
                ws.write(row + 2, 6, Formula("SUM($F11:$F%d)" % row))
                ws.write(row + 3, 5, 'Total')
                ws.write(row + 3, 6, Formula("SUM($G11:$G%d)" % row))
                ws.write(row + 4, 5, 'Costo Total')
                ws.write(row + 4, 6, Formula("SUM($H11:$H%d)" % row))
                ws.write(row + 5, 5, 'Total Utilidad')
                ws.write(row + 5, 6, Formula("SUM($I11:$I%d)" % row))
                ws.write(row + 6, 5, 'Comision Comercial')
                ws.write(row + 6, 6, Formula("SUM($J11:$J%d)" % row))

        file_data = StringIO.StringIO()
        wbk.save(file_data)
        return file_data.getvalue()
