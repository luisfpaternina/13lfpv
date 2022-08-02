# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

#Clase para heredar el modelo sale.order.line (ventas)
class EstimatedConfig(models.Model):
    _name = 'estimated.config'
    _inherit = 'mail.thread'
    
    #######
    name = fields.Char('Ingreso de estimación', tracking=True)
    active_estimate = fields.Boolean('Activo', tracking=True)
    profitability_1 = fields.Float('Rentabilidad 1', tracking=True)
    profitability_2 = fields.Float('Rentabilidad 2', tracking=True)
    profitability_3 = fields.Float('Rentabilidad 3', tracking=True)
    profitability_4 = fields.Float('Rentabilidad 4', tracking=True)
    ##########
    commission_1 = fields.Float('% commision 1', tracking=True)
    commission_2 = fields.Float('% commision 2', tracking=True)
    commission_3 = fields.Float('% commision 3', tracking=True)
    commission_4 = fields.Float('% commision 4', tracking=True)

    
    @api.model
    def create(self, vals):
        estimated_config_obj = self.env['estimated.config'].search([])
        if estimated_config_obj:                
            raise ValidationError('Solo se puede crear un registro de configuraciones estimadas')
        res = super(EstimatedConfig, self).create(vals)  # Save the form
        return res


    
#Clase para heredar el modelo sale.order.line (ventas)
class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'
    
    item = fields.Integer(string='Item')
    brand_id = fields.Many2one('product.brand', 'Marca')
    product_uom = fields.Many2one('uom.uom', 'U. Medida')
    u_value = fields.Float('Valor U.')
    discount_percent = fields.Float('% Descuento')
    price_total_related = fields.Float('Precio total')



#Clase para heredar el modelo sale.order (ventas)
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    contact_id = fields.Many2one('res.partner', 'contacto')
    #Agregado
    currency_sale = fields.Many2one('res.currency', 'Moneda')
    finish_date = fields.Date('Fecha de finalización')
    sales_category = fields.Selection([('switch','Switching'),('Route','Routing')], string="Categoría de venta")
    responsable1_user_id = fields.Many2one('res.users', string="Preventa 1")
    responsable2_user_id = fields.Many2one('res.users', string="Preventa 2")
    one_part = fields.Float(string="Part. 1 %")
    two_part = fields.Float(string="Part. 2 %", compute="_compute_one_part")
    payment_date_time = fields.Date(string="Fecha de pago")
    invoice_date = fields.Date("Fecha de factura")
    end_date =fields.Date("Fecha de finalización")
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
        ('other','Otros')], string="Categoría de venta")


    @api.constrains('one_part')
    def _check_one_part(self):
        for record in self:
            if record.one_part > 100 or record.one_part < 0:
                raise ValidationError("El valor debe estar en el rango de 0 a 100: %s" % record.one_part)


    @api.depends('one_part')
    def _compute_one_part(self):
        if self.one_part == 0:
            self.two_part = 100
        elif self.one_part > 0:
            self.two_part = 100.0 - self.one_part
        else:
            self.two_part = 0.0


    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_total_related
                amount_tax = amount_untaxed * 0.18
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })
    

    #Funcion para calcular utilizad, comisiones
    @api.depends('estimated_line.amount_utility', 'estimated_line.cost_total',
                 'estimated_line.price_total_w')
    def _compute_totals(self):
        logging.info('***********************_compute_totals*****************************')
        for record in self:
            record.total_utility = sum(line.amount_utility for line in record.estimated_line)
            record.cost_totals = sum(line.cost_total for line in record.estimated_line)
            record.price_totals = sum(line.price_total_w for line in record.estimated_line)
            logging.info('***********************FOR COMPUTE_TOTALS*****************************')
            logging.info('***********************FOR COMPUTE_TOTALS TOTAL UTILITY*****************************')
            logging.info(record.total_utility)
            logging.info(record.cost_totals)
            #record.commision = sum(line.commision for line in record.estimated_line)
            try:
                logging.info('***********************_compute_totals_try*****************************')
                logging.info(record.total_utility)
                logging.info(record.cost_totals)
                record.cost_effectiveness = round((record.total_utility / record.cost_totals * 100),2)
                logging.info('***********************COST EFEFECTIVENESS*****************************')
                logging.info(record.cost_effectiveness)
            except ZeroDivisionError:
                logging.info('***********************_compute_totals_except*****************************')
                record.cost_effectiveness = 0.0

            #record.commision_pre = record.total_utility * 0.02
    

    estimated_line = fields.One2many('estimated.sale', 'order_id',
                                     'Estimacion', readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     copy=True)
    ################################################################################
    # CAMPOS DE ESTIMACIÓN 
    ###############################################################################
    price_totals = fields.Float('Precio total', compute='_compute_totals')
    commision = fields.Char('C. Comercial', compute='_compute_comissions')
    commision_pre = fields.Char('C. Preventa', compute='_compute_comissions')
    total_utility = fields.Float('Utilidad', compute='_compute_totals')
    cost_effectiveness = fields.Float('Rentabilidad', compute='_compute_totals',
                                      store=True)
    cost_totals = fields.Float('Costo total', compute='_compute_totals')
    ###############################################################################
    #  CAMPOS DE ESTIMACIÓN REAL
    #################################################################################
    price_totals_real = fields.Float('Precio total', related='price_totals')
    commision_real = fields.Char('C. Comercial', store=True)
    commision_pre_real = fields.Char('C. Preventa', store=True)
    total_utility_real = fields.Float('Utilidad', store=True)
    cost_effectiveness_real = fields.Float('Rentabilidad', store=True)
    cost_totals_real = fields.Float('Costo total', store=True)
    ##################################################################################
    profitability_1 = fields.Float('Rentabilidad 1', compute='_compute_values_estimated')
    profitability_2 = fields.Float('Rentabilidad 2', compute='_compute_values_estimated')
    profitability_3 = fields.Float('Rentabilidad 3', compute='_compute_values_estimated')
    profitability_4 = fields.Float('Rentabilidad 4', compute='_compute_values_estimated')
    ##########
    commission_1 = fields.Float('% comision 1', compute='_compute_values_estimated')
    commission_2 = fields.Float('% comision 2', compute='_compute_values_estimated')
    commission_3 = fields.Float('% comision 3', compute='_compute_values_estimated')
    commission_4 = fields.Float('% comision 3', compute='_compute_values_estimated')
    
    @api.onchange('cost_totals_real')
    def _compute_totals_real(self):
        for record in self:
            logging.info('TEST PARA RESTA')
            logging.info(record.estimated_line)
            
            logging.info('TEST PRECIO TOTAL')
            logging.info(record.price_totals_real)
            
            logging.info('TEST COSTO TOTAL')
            logging.info(record.cost_totals_real)
            
            #record.total_utility_real = sum(line.amount_utility for line in record.estimated_line)
            #record.cost_totals_real = sum(line.cost_total for line in record.estimated_line)
            record.price_totals_real = sum(line.price_total_w for line in record.estimated_line)
            #record.commision = sum(line.commision for line in record.estimated_line)
            record.total_utility_real = record.price_totals_real - record.cost_totals_real
            try:
                record.cost_effectiveness_real = record.total_utility_real / record.cost_totals_real * 100
            except ZeroDivisionError:
                record.cost_effectiveness_real = 0.0
            logging.info('TEST PARA RECORD')
            logging.info('COSTO TOTAL')
            logging.info(record.cost_totals_real)
            logging.info('PRECIO TOTAL')
            logging.info(record.price_totals_real)
            logging.info('UTILIDAD')
            logging.info(record.total_utility_real)
            logging.info('RENTABILIDAD')
            logging.info(record.cost_effectiveness_real)
            sale_lines_utilities = [x.utility for x in record.estimated_line]
            if record.cost_effectiveness_real < record.profitability_3 and record.cost_effectiveness_real >= record.profitability_4:
                record.commision_real = 'Requiere Aprobación'
                record.commision_pre_real = 'Requiere Aprobación'
            
            else:
                if record.cost_effectiveness_real >= record.profitability_1:
                    c_value_1 = record.commission_1/100
                else:
                    c_value_1 = 1

                if record.cost_effectiveness_real < record.profitability_1 and record.cost_effectiveness_real >= record.profitability_2:
                    c_value_2 = record.commission_2/100
                else:
                    c_value_2 = 1

                if record.cost_effectiveness_real < record.profitability_2 and record.cost_effectiveness_real >= record.profitability_3:
                    c_value_3 = record.commission_3/100
                else:
                    c_value_3 = 1

                if record.cost_effectiveness_real < record.profitability_3:
                    c_value_4 = 0
                else:
                    c_value_4 = 1
                
                if record.cost_effectiveness_real >= record.profitability_3:
                    cr_value_4 = record.commission_4/100
                else:
                    cr_value_4 = 0 
                record.commision_real = str("{0:.2f}".format(c_value_1*c_value_2*c_value_3*c_value_4*record.price_totals_real))
                record.commision_pre_real = str("{0:.2f}".format(cr_value_4*record.price_totals_real))
            
            for utilities in sale_lines_utilities: 
                if utilities <= 5:
                    record.commision_real = 0
                    record.commision_pre_real = 0

    def _compute_values_estimated(self):
        estimated_config_obj = self.env['estimated.config'].search([])
        for record in self:
            if estimated_config_obj:
                estimated_line = estimated_config_obj[0]
                if estimated_line.active_estimate == True:
                    record.profitability_1 = estimated_line.profitability_1
                    record.profitability_2 = estimated_line.profitability_2
                    record.profitability_3 = estimated_line.profitability_3
                    record.profitability_4 = estimated_line.profitability_4
                    record.commission_1 = estimated_line.commission_1
                    record.commission_2 = estimated_line.commission_2
                    record.commission_3 = estimated_line.commission_3
                    record.commission_4 = estimated_line.commission_4
                else:
                    record.profitability_1 = 0
                    record.profitability_2 = 0
                    record.profitability_3 = 0
                    record.profitability_4 = 0
                    record.commission_1 = 0
                    record.commission_2 = 0
                    record.commission_3 = 0
                    record.commission_4 = 0
            else:
                record.profitability_1 = 0
                record.profitability_2 = 0
                record.profitability_3 = 0
                record.profitability_4 = 0
                record.commission_1 = 0
                record.commission_2 = 0
                record.commission_3 = 0
                record.commission_4 = 0
            
    
    @api.onchange('estimated_line')
    def _onchange_sale_line_items(self):
        if self.estimated_line:
            c = 1
            for line in self.estimated_line.sorted(lambda x: x.sequence):
                if line.item == 0:
                    line.item = c
                c += 1
    '''
    @api.depends('cost_effectiveness_real','profitability_1','profitability_2','profitability_3','commission_1','commission_2','commission_3')
    def _calculate_comissions(self):
        for record in self:
            logging.info('TEST PARA RECORD')
            logging.info('COSTO TOTAL')
            logging.info(record.cost_totals_real)
            logging.info('PRECIO TOTAL')
            logging.info(record.price_totals_real)
            logging.info('UTILIDAD')
            logging.info(record.total_utility_real)
            logging.info('RENTABILIDAD')
            logging.info(record.cost_effectiveness_real)
            sale_lines_utilities = [x.utility for x in record.estimated_line]
            if record.cost_effectiveness_real < record.profitability_2 and record.cost_effectiveness_real >= record.profitability_3:
                record.commision_real = 'Requiere Aprobación'
                record.commision_pre_real = 'Requiere Aprobación'

            else:
                if record.cost_effectiveness_real >=record.profitability_1:
                    c_value_1 = record.commission_1/100
                else:
                    c_value_1 = 1

                if record.cost_effectiveness_real < record.profitability_1 and record.cost_effectiveness_real >= record.profitability_2:
                      c_value_2 = record.commission_2/100
                else:
                    c_value_2 = 1

                if record.cost_effectiveness_real < record.profitability_2:
                    c_value_3 = 0
                else:
                    c_value_3 = 1

                if record.cost_effectiveness_real >= record.profitability_2:
                    cr_value_1 = record.commission_3/100
                else:
                    cr_value_1 = 0 

                record.commision_real = str("{0:.2f}".format(c_value_1*c_value_2*c_value_3*record.price_totals_real))
                record.commision_pre_real = str("{0:.2f}".format(cr_value_1*record.price_totals_real))

            for utilities in sale_lines_utilities: 
                if utilities <= 5:
                    record.commision_real = 0
                    record.commision_pre_real = 0
    '''
    
    @api.depends('cost_effectiveness','profitability_1','profitability_2','profitability_3','profitability_4','commission_1','commission_2','commission_3','commission_4')
    def _compute_comissions(self):
            
        for record in self:
            sale_lines_utilities = [x.utility for x in record.estimated_line]
            #sale_lines = record.env['estimated.sale'].search([('id','=',record.estimated_line.id)])
            logging.info('RENTABILIDAD')
            logging.info(record.profitability_1)
            logging.info(record.profitability_2)
            logging.info(record.profitability_3)
            logging.info(record.profitability_4)
            logging.info('COMISIONES')
            logging.info(record.commission_1)
            logging.info(record.commission_2)
            logging.info(record.commission_3)
            logging.info(record.commission_4)
            
            if record.cost_effectiveness < record.profitability_3 and record.cost_effectiveness >= record.profitability_4:
                record.commision = 'Requiere Aprobación'
                record.commision_pre = 'Requiere Aprobación'
            
            else:
                if record.cost_effectiveness >= record.profitability_1:
                    c_value_1 = record.commission_1/100
                else:
                    c_value_1 = 1

                if record.cost_effectiveness < record.profitability_1 and record.cost_effectiveness >= record.profitability_2:
                    c_value_2 = record.commission_2/100
                else:
                    c_value_2 = 1

                if record.cost_effectiveness < record.profitability_2 and record.cost_effectiveness >= record.profitability_3:
                    c_value_3 = record.commission_3/100
                else:
                    c_value_3 = 1

                if record.cost_effectiveness < record.profitability_3:
                    c_value_4 = 0
                else:
                    c_value_4 = 1
                
                if record.cost_effectiveness >= record.profitability_3:
                    cr_value_4 = record.commission_4/100
                else:
                    cr_value_4 = 0 
                record.commision = str("{0:.2f}".format(c_value_1*c_value_2*c_value_3*c_value_4*record.price_totals))
                record.commision_pre = str("{0:.2f}".format(cr_value_4*record.price_totals))
            """
            for utilities in sale_lines_utilities: 
                if utilities <= 5:
                    record.commision = 0
                    record.commision_pre = 0
            """
    
            
    def send_order_line(self):
        order_line = []
        for record in self:
            if record.cost_effectiveness < 0.00:
                raise ValidationError(_('La rentabilidad no puede ser menor a 0.00'))

            if record.order_line:
                for line in record.order_line:
                    line.unlink()

            for sale_line in record.estimated_line:
                product_obj = record.env['product.product'].search([('name','=', sale_line.product_id.name)])
                line = []
                values = {
                    'item': sale_line.item,
                    'product_id': product_obj.id,
                    'name': sale_line.name,
                    'brand_id': sale_line.brand_id.id,
                    'u_value': sale_line.u_value,
                    'discount': sale_line.discount,
                    'discount_percent': sale_line.discount_percent,
                    'product_uom_qty': sale_line.qty,
                    'product_uom': sale_line.product_uom.id,
                    'price_unit': sale_line.price_unit,
                    'price_total_related': sale_line.price_total,
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
    cost_total1 = fields.Float('Costo total')
    price_total1 = fields.Float('Precio total')
    amount_utility = fields.Float('Utilidad', compute='_compute_cost_net_unit')
    amount_utility1 = fields.Float('Utilidad')
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
                record.brand_id = record.product_id.brand_id.id
                if record.product_id.description_sale:
                    record.name = record.product_id.description_sale
                else:
                    record.name = record.product_id.name
