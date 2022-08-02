# -*- coding: utf-8 -*-


from odoo import models, fields, api
from xlwt import easyxf, Workbook
from datetime import datetime

import base64
import StringIO


MONTHS = {
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April': 'Abril',
    'May': 'Mayo',
    'June': 'Junio',
    'July': 'Julio',
    'August': 'Agosto',
    'September': 'Setiembre',
    'October': 'Octubre',
    'November': 'Noviembre',
    'December': 'Diciembre'
}


class CustomersAccordance(models.Model):
    _name = 'customers.accordance'

    name = fields.Char('Correlativo', default='/')
    date_start = fields.Date('Fecha inicio', required=True)
    date_stop = fields.Date('Fecha fin', required=True)
    project_id = fields.Many2one('project.project', 'Proyecto')
    purchase_id = fields.Many2one('purchase.order', 'Orden compra', required=True,
                                  domain=[('state', 'not in', ('draft', 'sent', 'bid', 'confirmed', 'cancel'))])
    sale_id = fields.Many2one('sale.order', 'Pedido venta')
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('customers.accordance'))
    customer_id = fields.Many2one('res.partner', 'Cliente')
    line_accordance_ids = fields.One2many('line.accordance', 'customers_accordance_id',
                                          'Detalle')
    price_total = fields.Float(string='Precio + IGV', readonly=True,
                               compute='_get_total')
    sign_line = fields.One2many('sign.accordance', 'customers_accordance_id', 'Firmas')
    description = fields.Char('Descripcion', required=True)
    header = fields.Char('Cabecera', required=True)

    @api.depends('sale_id')
    def _get_total(self):
        self.price_total = self.sale_id.amount_total

    @api.model
    def create(self, values):
        sequence = self.env['ir.sequence']
        sequence = sequence.get('CustomersAccordance')
        values.update({
            'name': sequence
        })
        return super(CustomersAccordance, self).create(values)

    @api.multi
    def report_xls(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_xls?model=customers.accordance&field=name&id=%s&filename=demo' % self.id,
            'target': 'self'
        }

    @api.multi
    def get_filename(self):
        return 'Reporte.xls'

    @api.multi
    def _get_content(self):
        text1 = """El presente documento representa la aceptacion y conformidad en la ejecucion de las actividades relacionadas al
servicio de: %s realizado del %s al %s con el siguiente detalle"""

        text2= """El servicio comprende los siguientes entregables:"""

        text3 = """El usuario final certifica que la totalidad de productos descritos en la presente acta de recepcion, han sido entregados
y terminados y que, habiendo sido sometidos a las pruebas de validacion y aceptacion indicadas, estan de acuerdo con las
especificaciones formales y demas requisitos convenidos y establecidos entre las partes, acreditando que la prestacion se
efectuo sin incurrir en penalidad alguna."""

        for obj in self:
            style1 = easyxf('align: wrap on, horiz justified;''borders: left thin, right thin, top thin, bottom thin')
            style2 = easyxf('font: height 160, name Arial, bold on;''align: wrap on, vert centre, horiz center;''borders: left thin, right thin, top thin, bottom thin')
            style3 = easyxf('font: height 180, name Arial, bold on;''align: wrap on, vert centre, horiz center;')
            style4 = easyxf('font: height 180, name Arial, bold on;''align: wrap on, vert centre, horiz center;''borders: left thin, right thin, top thin, bottom thin')
            style5 = easyxf('font: height 180, name Arial, bold on;')

            wbk = Workbook()
            date_start = datetime.strptime(obj.date_start, '%Y-%m-%d').strftime('%B')
            year_start = datetime.strptime(obj.date_start, '%Y-%m-%d').strftime('%Y')
            year_date = datetime.strptime(obj.date_start, '%Y-%m-%d').strftime('%d')
            ws = wbk.add_sheet('demo')
            ws.write_merge(1, 2, 1, 3, 'Logo Cliente', style1)
            ws.write_merge(1, 2, 4, 6, '%s' % obj.header, style1)
            ws.write_merge(1, 2, 7, 9, 'Logo INET', style1)
            ws.write_merge(5, 5, 3, 7, 'Acta de Conformidad', style3)
            ws.write_merge(6, 6, 7, 9, 'Lima, %s de %s del %s' % (year_date, date_start, year_start))
            ws.write_merge(8, 8, 1, 9,  text1 % (obj.description, obj.date_start, obj.date_stop))
            ws.write_merge(10, 10, 1, 2, 'N Pedido:')
            ws.write_merge(10, 10, 3, 6, obj.sale_id.name)
            ws.write_merge(11, 11, 1, 2, 'Proyecto:')
            ws.write_merge(11, 11, 3, 6, obj.project_id.name)
            ws.write_merge(12, 12, 1, 2, 'Cliente:')
            ws.write_merge(12, 12, 3, 6, obj.customer_id.name)
            ws.write_merge(13, 13, 1, 2, 'N Orden de compra:')
            ws.write_merge(13, 13, 3, 6, obj.purchase_id.name)
            ws.write_merge(14, 14, 1, 2, 'Precio + IGV:')
            ws.write_merge(14, 14, 3, 3, '%s %s' % (obj.sale_id.currency_id. symbol, '{0:.2f}'.format(obj.price_total)))
            ws.write_merge(16, 16, 1, 9, text2, style5)

            ws.row(2).height = 1000
            ws.row(8).height = 500
            ws.row(16).height = 500
            ws.row(21).height = 900

            row = 18
            for accordance in obj.line_accordance_ids:
                ws.write_merge(row, row, 1, 9, accordance.name, style1)
                row += 1

            row += 1

            ws.write_merge(row, row, 1, 9, text3)

            row += 2

            ws.write_merge(row, row, 1, 5, 'Firmas de Aprobacion:', style5)

            row += 3

            ws.write_merge(row, row, 1, 3, 'Nombre / Rol', style4)
            ws.write_merge(row, row, 4, 6, 'Firma', style4)
            ws.write_merge(row, row, 7, 9, 'Fecha', style4)

            row += 1

            for line in obj.sign_line:
                ws.row(row).height = 700
                name = """%s
        %s
        %s"""

                company = line.partner_id.company_id.name
                if line.partner_id.parent_id:
                    company = line.partner_id.parent_id.name
                ws.write_merge(row, row, 1, 3, name % (line.partner_id.name,
                                                       line.partner_id.function,
                                                       company), style2)
                ws.write_merge(row, row, 4, 6, None, style2)
                ws.write_merge(row, row, 7, 9, line.date_sign, style2)
                row += 1

            file_data = StringIO.StringIO()
            wbk.save(file_data)
            filecontent = file_data.getvalue()
            return filecontent


class LineAccordance(models.Model):
    _name = 'line.accordance'

    name = fields.Char('Descripcion')
    customers_accordance_id = fields.Many2one('customers.accordance')


class SignAccordance(models.Model):
    _name = 'sign.accordance'

    partner_id = fields.Many2one('res.partner', 'Cliente')
    date_sign = fields.Date('Fecha')
    customers_accordance_id = fields.Many2one('customers.accordance')
