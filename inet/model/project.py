# -*- coding: utf-8 -*-


from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    note = fields.Char('Nota')
