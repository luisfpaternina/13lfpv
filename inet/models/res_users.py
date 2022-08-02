# coding: utf-8

from odoo import models, api, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    mobile = fields.Char('Telefono movil')

    @api.model
    def create(self, values):
        user_id = super(ResUsers, self).create(values)
        user = self.browse(user_id.id)
        if user.partner_id.company_id:
            user.partner_id.write({'mobile': values.get('mobile', False)})
        return user_id

    
    def write(self, values):
        if 'mobile' in values:
            user = self.browse(self.id)
            user.partner_id.write({'mobile': values.get('mobile')})
        return super(ResUsers, self).write(values)
