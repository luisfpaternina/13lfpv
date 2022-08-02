# coding: utf-8
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2016 Pypelab SAC - pimentelrojas@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'INET PERU',
    'version': "1.0",
    'author': 'Pypelab SAC',
    'website': '',
    'mail': 'pimentelrojas@gmail.com',
    'category': 'account',
    'depends': [
        "base", "stock", "account", "sale_management", "purchase"
    ],
    'description': 'Modulo personalizado para INET PERU',
    'data': [
        "security/inet_security.xml",
        "security/ir.model.access.csv", 
        "view/product_view.xml",
        "view/estimated_config_view.xml",
        #"view/account_invoice_view.xml",
        "view/sale_order_view.xml",
        "view/purchase_order_view.xml",
        #"view/report_purchase_order_view.xml",
        #"view/external_layout_header.xml",
        #"view/res_users_view.xml",
        "view/report_sale_order_view.xml",
        #"data/inet_data_view.xml",
        #"view/report_purchase2_order_view.xml",
        #"view/accordance_order_view.xml",
        #"view/report_accordance_order_view.xml",
        #"view/customers_accordance_view.xml",
        #"view/report_customers_accordance_view.xml",
        #"view/res_partner_view.xml",
        "view/report_sale_wizard.xml",
        #"view/report_purchase_wizard.xml",
        #"view/aging_receivable_wizard.xml",
        #"view/aging_pay_wizard.xml",
        #"view/project_view.xml"
        "view/sale_portal_templates.xml"
    ],
    'auto_install': True
}
