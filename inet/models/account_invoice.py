# coding: utf-8


from odoo import models, fields, api
from datetime import datetime, timedelta


class AccountInvoce(models.Model):
    _inherit = 'account.move'

    number_out = fields.Char('Numero guia')
    motive = fields.Char('Motivo')
    customer = fields.Many2one('res.partner', 'Cliente',
                               domain=[('customer', '=', True)])
    delivered = fields.Selection([('delivered', 'Entregado'),
                                  ('by_delivered', 'Por entregar')], 'Monto')
    sale_id = fields.Many2one('sale.order', 'Pedido venta')
    date_reception = fields.Date('Fecha recepcion')
    date_due2 = fields.Date('F. venc Real')

    @api.onchange('date_reception', 'payment_term')
    def _date_due2(self):
        payment_line = self.env['account.payment.term.line']
        domain = [('payment_id', '=', self.payment_term.id)]
        obj_term_line = payment_line.search(domain, limit=1)
        days = obj_term_line.days if obj_term_line.exists() else 0
        if self.date_reception:
            date_reception = self.date_reception
            date_reception = datetime.strptime(date_reception, '%Y-%m-%d')
            date_reception = date_reception + timedelta(days=days)
            self.date_due2 = date_reception.strftime('%Y-%m-%d')

    
    def invoice_validate(self):
        inv_line = self.env['account.move.line']
        for self_obj in self:
            count = 1
            for line in self_obj.invoice_line:
                inv_line.browse(line.id).write({'number_item': count})
                count += 1
        return super(AccountInvoce, self).invoice_validate()

    
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        result = super(AccountInvoce, self).onchange_partner_id(type=type,
                                                                partner_id=partner_id,
                                                                date_invoice=date_invoice,
                                                                payment_term=payment_term,
                                                                partner_bank_id=partner_bank_id,
                                                                company_id=company_id)
        if partner_id:
            obj_partner = self.env['res.partner'].browse(partner_id)
            if obj_partner.name == 'MOVILIDAD':
                sequence = self.env['ir.sequence']
                sequence = sequence.get('mobility')
                result['value'].update({
                    'supplier_invoice_number': sequence
                })
        return result


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    number_item = fields.Integer('Nro item', readonly="True", copy=False)
