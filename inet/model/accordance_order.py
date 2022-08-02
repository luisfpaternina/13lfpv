# -*- coding: utf-8 -*-


from odoo import models, api, fields, _


class AccordanceOrder(models.Model):
    _name = 'accordance.order'

    name = fields.Char('Correlativo', default='/')
    date_start = fields.Date('Fecha inicio', required=True)
    date_stop = fields.Date('Fecha fin', required=True)
    purchase_id = fields.Many2one('purchase.order', 'Orden compra', required=True,
                                  domain=[('state', 'not in', ('draft','sent','bid', 'confirmed', 'cancel'))])
    document_ids = fields.Many2many('document.relationship', 'accordance_documen_relationship',
                                    'accordance_id', 'document_relationship_id',
                                    string='Documentos relacionados')
    company_id = fields.Many2one('res.company', 'Compañia', required=True,
                                  default=lambda self: self.env['res.company']._company_default_get('accordance.order'))
    sale_id = fields.Many2one('sale.order', 'Pedido de venta', required=True)
    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True)
    work_done = fields.Char('Trabajo realizado')
    others = fields.Text('Otros')

    @api.model
    def create(self, values):
        sequence = self.env['ir.sequence']
        sequence = sequence.get('accordance')
        values.update({
            'name': sequence
        })
        return super(AccordanceOrder, self).create(values)


class DocumentRelationShip(models.Model):
    _name = 'document.relationship'

    name = fields.Char('Nombre')
