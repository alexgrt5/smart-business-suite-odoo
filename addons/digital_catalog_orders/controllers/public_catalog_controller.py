import json
from odoo import http
from odoo.http import request


class PublicCatalogController(http.Controller):

    @http.route(['/catalogo/<string:slug>'], type='http', auth='public', website=True)
    def catalog_page(self, slug, **kwargs):
        catalog = request.env['digital.catalog'].sudo().search([
            ('slug', '=', slug),
            ('active', '=', True)
        ], limit=1)

        if not catalog:
            return request.not_found()

        return request.render('digital_catalog_orders.catalog_page', {
            'catalog': catalog
        })

    @http.route(['/catalogo/<string:slug>/pedido'], type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def create_catalog_order(self, slug, **post):
        catalog = request.env['digital.catalog'].sudo().search([
            ('slug', '=', slug),
            ('active', '=', True),
            ('allow_orders', '=', True)
        ], limit=1)

        if not catalog:
            return request.not_found()

        cart_data = json.loads(post.get('cart_data', '[]'))

        if not cart_data:
            return request.redirect(f'/catalogo/{slug}')

        order = request.env['digital.catalog.order'].sudo().create({
            'catalog_id': catalog.id,
            'partner_name': post.get('partner_name'),
            'partner_phone': post.get('partner_phone'),
            'partner_email': post.get('partner_email'),
            'delivery_type': post.get('delivery_type'),
            'delivery_address': post.get('delivery_address'),
            'notes': post.get('notes'),
            'line_ids': [
                (0, 0, {
                    'product_id': int(item.get('product_id')),
                    'quantity': float(item.get('quantity')),
                    'price_unit': float(item.get('price_unit')),
                })
                for item in cart_data
            ]
        })

        order.action_confirm()

        return request.render('digital_catalog_orders.catalog_order_success', {
            'order': order,
            'catalog': catalog
        })