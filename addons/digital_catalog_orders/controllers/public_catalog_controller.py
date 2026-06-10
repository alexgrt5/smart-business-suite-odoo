from odoo import http
from odoo.http import request


class PublicCatalogController(http.Controller):

    @http.route(
        ['/catalogo/<string:slug>'],
        type='http',
        auth='public',
        website=True
    )
    def catalog_page(self, slug, **kwargs):

        catalog = request.env['digital.catalog'].sudo().search([
            ('slug', '=', slug),
            ('active', '=', True)
        ], limit=1)

        if not catalog:
            return request.not_found()

        return request.render(
            'digital_catalog_orders.catalog_page',
            {
                'catalog': catalog
            }
        )