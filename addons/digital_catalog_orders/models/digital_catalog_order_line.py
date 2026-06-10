from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DigitalCatalogOrderLine(models.Model):
    _name = 'digital.catalog.order.line'
    _description = 'Digital Catalog Order Line'

    order_id = fields.Many2one('digital.catalog.order', string='Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.template', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError('Quantity must be greater than zero.')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.price_unit = line.product_id.list_price