# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

#Clase para heredar el modelo sale.order.line (ventas)
class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'
    
    brand_id = fields.Many2one('product.brand', 'Marca')
    product_uom = fields.Many2one('uom.uom', 'U. Medida')
    u_value = fields.Float('Valor U.')
    discount_percent = fields.Float('% Descuento')
    price_total_related = fields.Float('Precio total')
#Clase para heredar el modelo sale.order (ventas)
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    contact_id = fields.Many2one('res.partner', 'contacto')
    
    #Funcion para calcular utilizad, comisiones
    @api.depends('estimated_line.amount_utility', 'estimated_line.cost_total',
                 'estimated_line.price_total_w')
    def _compute_totals(self):
        for record in self:
            record.total_utility = sum(line.amount_utility for line in record.estimated_line)
            record.cost_totals = sum(line.cost_total for line in record.estimated_line)
            record.price_totals = sum(line.price_total_w for line in record.estimated_line)
            #record.commision = sum(line.commision for line in record.estimated_line)
            try:
                record.cost_effectiveness = record.total_utility / record.cost_totals * 100
            except ZeroDivisionError:
                record.cost_effectiveness = 0.0

            #record.commision_pre = record.total_utility * 0.02
    
    #campos
    estimated_line = fields.One2many('estimated.sale', 'order_id',
                                     'Estimacion', readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     copy=True)
    #######
    profitability_1 = fields.Float('Rentabilidad 1')
    profitability_2 = fields.Float('Rentabilidad 2')
    profitability_3 = fields.Float('Rentabilidad 3')
    ##########
    commission_1 = fields.Float('% commission 1')
    commission_2 = fields.Float('% commission 2')
    commission_3 = fields.Float('% commission 4')
    cost_totals = fields.Float('Costo total', compute='_compute_totals')
    price_totals = fields.Float('Precio total', compute='_compute_totals')
    commision = fields.Char('C. Comercial', compute='_compute_comissions')
    commision_pre = fields.Char('C. Preventa', compute='_compute_comissions')
    total_utility = fields.Float('Utilidad', compute='_compute_totals')
    cost_effectiveness = fields.Float('Rentabilidad', compute='_compute_totals',
                                      store=True)
    
    
    
    @api.onchange('estimated_line')
    def _onchange_sale_line_items(self):
        if self.estimated_line:
            c = 1
            for line in self.estimated_line.sorted(lambda x: x.sequence):
                if line.item == 0:
                    line.item = c
                c += 1

    @api.depends('cost_effectiveness','profitability_1','profitability_2','profitability_3','commission_1','commission_2','commission_3')
    def _compute_comissions(self):  
        
        for record in self:
            sale_lines_utilities = [x.utility for x in record.estimated_line]
           # sale_lines = record.env['estimated.sale'].search([('id','=',record.estimated_line.id)])

            if record.cost_effectiveness < record.profitability_2 and record.cost_effectiveness >= record.commission_3:
                record.commision = 'Requiere Aprobación'
                record.commision_pre = 'Requiere Aprobación'
            else:
                if record.cost_effectiveness >=record.profitability_1:
                    c_value_1 = record.commission_1/100
                else:
                    c_value_1 = 1

                if record.cost_effectiveness < record.profitability_1 and record.cost_effectiveness >= record.profitability_2:
                    c_value_2 = record.commission_2/100
                else:
                    c_value_2 = 1

                if record.cost_effectiveness < record.profitability_2:
                    c_value_3 = 0
                else:
                    c_value_3 = 1

                if record.cost_effectiveness >= record.profitability_2:
                    cr_value_1 = record.commission_3/100
                else:
                    cr_value_1 = 0
            
            record.commision = str(c_value_1*c_value_2*c_value_3*record.price_totals)
            record.commision_pre = str(cr_value_1*record.price_totals)
            
            for utilities in sale_lines_utilities: 
                if utilities <= 5:
                    record.commision = 0
                    record.commision_pre = 0

            
    def send_order_line(self):
        order_line = []
        for record in self:
            if record.cost_effectiveness < 0.00:
                raise ValidationError(_('La rentabilidad no puede ser menor a 0.00'))

            if record.order_line:
                for line in record.order_line:
                    line.unlink()

            for sale_line in record.estimated_line:
                line = []
                values = {
                    'product_id': sale_line.product_id.id,
                    'name': sale_line.name,
                    'brand_id': sale_line.brand_id.id,
                    'u_value': sale_line.u_value,
                    'discount': sale_line.discount,
                    'discount_percent': sale_line.discount_percent,
                    'product_uom_qty': sale_line.qty,
                    'product_uom': sale_line.product_uom.id,
                    'price_unit': sale_line.price_unit,
                    'price_total_related': sale_line.price_total,
                    #'delay': sale_line.product_id.sale_delay,
                    'tax_id': [(6, 0, [x.id for x in sale_line.product_id.taxes_id])]
                }
                line.append(False),
                line.append(False)
                line.append(values)
                order_line.append(line)
            return record.write({'order_line': order_line})

#clase para crear una nueva tabla en la base de datos
class EstimatedSale(models.Model):
    _name = 'estimated.sale'
    _description = 'estimated sale'

    
    product_id = fields.Many2one('product.template', 'Código')
    brand_id = fields.Many2one('product.brand', 'Marca')
    product_uom = fields.Many2one('uom.uom', 'U. Medida')
    cost_unit = fields.Float('Costo U')
    product_uom_qty = fields.Float('% Import.')
    cost_net_unit = fields.Float('Costo neto U.', compute='_compute_cost_net_unit')
    utility = fields.Float('% Utilidad')
    u_value = fields.Float('Valor U.')
    discount_percent = fields.Float('% Descuento')
    discount = fields.Float('Descuento')
    price_unit = fields.Float('Precio U.', compute='_compute_cost_net_unit')
    order_id = fields.Many2one('sale.order','Pedida de venta')
    cost_total = fields.Float('Costo total', compute='_compute_cost_net_unit')
    price_total = fields.Float('Precio total', compute='_compute_cost_net_unit')
    amount_utility = fields.Float('Utilidad', compute='_compute_cost_net_unit')
    #commision = fields.Float('Comision', compute='_compute_cost_net_unit')
    name = fields.Text('Descripción')
    price_total_w = fields.Float('Sin dscto', compute='_compute_cost_net_unit')
    qty = fields.Float('Cantidad')
    item = fields.Integer(string='Item')
    sequence = fields.Integer(string='Secuencia')
    
    @api.depends('product_uom_qty', 'cost_unit', 'qty', 'utility')
    def _compute_cost_net_unit(self):
        for obj in self:
            obj.cost_net_unit = obj.cost_unit * (1+obj.product_uom_qty/100)
            obj.u_value = obj.cost_net_unit * (1+(obj.utility/100))
            obj.discount = obj.u_value * (obj.discount_percent/100) 
            obj.price_unit = obj.u_value * (1-obj.discount_percent/100)
            obj.cost_total = obj.cost_net_unit * obj.qty
            obj.price_total = obj.price_unit * obj.qty
            obj.price_total_w = obj.price_unit * obj.qty
            obj.amount_utility = obj.price_total - obj.cost_total
            #obj.commision = obj.amount_utility * 0.1
    
    
    @api.onchange('product_id')
    def onchange_product_cost(self):
        for record in self:
            if record.product_id:
                record.cost_unit = record.product_id.standard_price
                record.product_uom = record.product_id.uom_id
                if record.product_id.description_sale:
                    record.name = record.product_id.description_sale
                else:
                    record.name = record.product_id.name

    
