# -*- coding: utf-8 -*-


from odoo import models, fields
from xlwt import Formula, easyxf, Workbook
from datetime import datetime, timedelta

import StringIO


class AgingPay(models.TransientModel):
    _name = 'aging.pay'

    company_id = fields.Many2one('res.company', 'Compañia', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('aging.receivable'))
    date_from = fields.Date('Fecha inicio')
    date_to = fields.Date('Fecha fin')
    partner_id = fields.Many2one('res.partner', 'Empresa',
                                 domain=[('supplier', '=', True)])
    range_date = fields.Boolean('Rango')


class AgingPayXls(models.AbstractModel):
    _inherit = 'download.file.base.model'
    _name = 'aging.pay.xls'

    def init(self, record_id):
        super(AgingPayXls, self).init(record_id)

    def get_filename(self):
        return 'PorPagar.xls'

    def get_content(self):
        invoice = self.env['account.invoice']
        reg_aging = self.env['aging.pay'].browse(self.record_id)

        domain = [('company_id', '=', reg_aging.company_id.id),
                  ('type', 'in', ('in_invoice', 'in_refund')),
                  ('state', '!=', 'cancel')]

        if reg_aging.partner_id:
            domain.append(('partner_id', '=', reg_aging.partner_id.id))

        if reg_aging.range_date:
            domain.append(('date_due2', '>=', reg_aging.date_from))
            domain.append(('date_due2', '<=', reg_aging.date_to))

        wbk = Workbook()
        style0 = easyxf('font: height 160, name Times new Roman, bold on;''align: wrap on, horiz justified;')
        style1 = easyxf('font: height 160, name Times new Roman, bold on;''align: wrap on, horiz justified;''borders: left thin, right thin, top thin, bottom thin')
        style2 = easyxf('font: height 200, name Times new Roman, bold on;''borders: top thin;', num_format_str='0.00')
        style3 = easyxf(num_format_str='0.00')

        ws = wbk.add_sheet('Anticuamiento por Pagar')

        s0 = 0
        s1 = 1
        s2 = 2
        s3 = 3
        s4 = 4
        s5 = 5

        ws.col(1).width = 6000
        ws.col(2).width = 10000
        ws.col(6).width = 6000
        # ws.col(7).width = 10000
        ws.col(8).width = 5000

        ws.write_merge(s0, s0, 0, 1, 'ANTICUAMIENTO DE PAGO', style0)
        ws.write_merge(s1, s1, 0, 1,  reg_aging.company_id.name, style0)
        ws.write(s2, 4, datetime.now().strftime('%Y-%m-%d'))
        ws.write(s3, 0, 'F. RECEPCION', style1)
        ws.write(s3, 1, 'RUC', style1)
        ws.write(s3, 2, 'RAZON SOCIAL', style1)
        ws.write(s3, 3, 'PLAZO', style1)
        ws.write(s3, 4, 'DIAS', style1)
        ws.write(s3, 5, 'VCTO', style1)
        ws.write(s3, 6, 'N° DOCUMENTO'.decode('utf-8'), style1)
        ws.write(s3, 7, 'DIVISA', style1)
        ws.write(s3, 8, 'TIPO DE CAMBIO', style1)
        ws.write(s3, 9, 'IMPORTE ORIGINAL', style1)
        ws.write(s3, 10, 'PAGOS A CUENTA', style1)
        ws.write(s3, 11, 'SALDO', style1)
        ws.write(s3, 12, 'ESTADO', style1)
        ws.write(s3, 13, 'FECHA VENCIMIENTO REAL', style1)

        obj_invoice = invoice.search(domain)
        if obj_invoice:
            for invoices in obj_invoice:
                days = 0
                domain = [('payment_id', '=', invoices.payment_term.id)]
                payment_term = self.env['account.payment.term.line'].search(domain,
                                                                            limit=1)

                state = 'Por Pagar' if invoices.state == 'draft' or invoices.state == 'open' else 'Pagado'
                date_reception = invoices.date_reception

                if payment_term.exists():
                    days = payment_term.days

                ws.write(s4, 0, invoices.date_reception)
                ws.write(s4, 1, invoices.partner_id.vat)
                ws.write(s4, 2, invoices.partner_id.name)
                ws.write(s4, 3, int(days))
                ws.write(s4, 4, Formula("$E$3-$A%d" % s5))
                ws.write(s4, 5, Formula("$E%d-$D%d" % (s5, s5)))
                ws.write(s4, 6, invoices.voucher_number)
                ws.write(s4, 7, invoices.currency_id.name)
                ws.write(s4, 8, invoices.exchange_rate)
                ws.write(s4, 9, invoices.amount_total, style3)
                ws.write(s4, 10, Formula("$J%d-$L%d" % (s5, s5)), style3)
                ws.write(s4, 11, invoices.residual, style3)
                ws.write(s4, 12, state)
                ws.write(s4, 13, invoices.date_due2)
                s4 += 1
                s5 += 1

        file_data = StringIO.StringIO()
        wbk.save(file_data)
        return file_data.getvalue()
