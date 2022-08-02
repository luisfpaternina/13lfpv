# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

#Clase para heredar el modelo sale.order (ventas)
class AccountPeriod(models.Model):
    _name = 'account.period'
    
    name = fields.Char(string="Nombre")
    period_start = fields.Date('Inicio', required=True)
    period_end = fields.Date('Fin', required=True)