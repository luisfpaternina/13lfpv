# -*- coding: utf-8 -*-


from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition


class DownloadXls(http.Controller):
    @http.route('/web/binary/download_xls', type='http', auth='user')
    @serialize_exception
    def download_xls(self, model, field, id, filename=None, **kw):
        Model = request.registry[model]
        cr, uid, context = request.cr, request.uid, request.context

        content = Model._get_content(cr, uid, int(id))

        if not content:
            return request.not_found()
        else:
            filename = Model.get_filename(cr, uid, int(id))
            return request.make_response(content,
                                         [('Content-Type', 'application/octet-stream;charset=utf-8;'),
                                          ('Content-Disposition', u'attachment; filename=%s;' % content_disposition(filename))])


class ReportSaleXls(http.Controller):
    @http.route('/web/binary/report_sale', type='http', auth='user')
    @serialize_exception
    def report_sale(self, model, field, id, filename=None, **kw):
        Model = request.registry[model]
        cr, uid, context = request.cr, request.uid, request.context

        content = Model._get_content(cr, uid, int(id))

        if not content:
            return request.not_found()
        else:
            filename = Model.get_filename(cr, uid, int(id))
            return request.make_response(content,
                                         [('Content-Type', 'application/octet-stream;charset=utf-8;'),
                                          ('Content-Disposition', u'attachment; filename=%s;' % content_disposition(filename))])


"""class ReportPurchaseXls(http.Controller):
    @http.route('/web/binary/report_purchase', type='http', auth='user')
    @serialize_exception
    def report_purchase(self, model, field, id, filename=None, **kw):
        Model = request.registry[model]
        cr, uid, context = request.cr, request.uid, request.context

        content = Model._get_content(cr, uid, int(id))

        if not content:
            return request.not_found()
        else:
            filename = Model.get_filename(cr, uid, int(id))
            return request.make_response(content,
                                         [('Content-Type', 'application/octet-stream;charset=utf-8;'),
                                          ('Content-Disposition', u'attachment; filename=%s;' % content_disposition(filename))])"""
