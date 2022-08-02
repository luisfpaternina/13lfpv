# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    paid_method = fields.Selection([('transfer', 'Transferencia'),
                                    ('voucher', 'cheques'),
                                    ('others', 'Otros')], 'Metodo de pago')
    contact_id = fields.Many2one('res.partner', 'Contacto')
    responsible_id = fields.Many2one('res.users', 'Realizado por')
    department_id = fields.Many2one('hr.department', 'Departamento')
    phone = fields.Char('Telefono')
    project_id = fields.Many2one('project.project', 'Proyecto')
    sale_id = fields.Many2one('sale.order', 'Pedido de venta')
    date_start = fields.Date('Fecha inicio')
    date_finish = fields.Date('Fecha fin')
    accordance = fields.Char('Correlativo')
    estimated_category = fields.Selection([
        ('s','Switching'),
        ('r','Routing'),
        ('w','Wireless'),
        ('sr','Seguridad de Red'),
        ('server','Servidores'),
        ('storage','Storage'),
        ('cloud','Cloud'),
        ('hp','Hiperconvergencia'),
        ('v','Virtualización'),
        ('license','Licencias'),
        ('alquiler','Alquileres'),
        ('services','Servicios de mantenimiento'),
        ('support','Servicio de Soporte'),
        ('settings','Servicio de configuración'),
        ('ph','Telefonía'),
        ('ce','Cableado estructurado'),
        ('cctv','CCTV'),
        ('se','Sistemas eléctricos'),
        ('air','Aire acondicionado'),
        ('sdi','Sistema de detección de incendio'),
        ('other','Otros')], string="Categoría de compra")
    

    @api.onchange('responsible_id')
    def onchange_department(self):
        obj_employee = self.env['hr.employee']
        employee = obj_employee.search([('user_id', '=', self.responsible_id.id)], limit=1)
        if employee.exists():
            self.department_id = employee.department_id.id
            self.phone = employee.mobile_phone
        else:
            self.department_id = False
            self.phone = False


    def get_accordance(self):
        for obj in self:
            if not obj.accordance:
                sequence = self.env['ir.sequence']
                sequence = sequence.get('accordance')
                return self.write({'accordance': sequence})
            else:
                return False
