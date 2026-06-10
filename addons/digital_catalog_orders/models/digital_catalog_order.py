from odoo import api, fields, models
from odoo.exceptions import UserError


class DigitalCatalogOrder(models.Model):
    _name = 'digital.catalog.order'
    _description = 'Digital Catalog Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Referencia del pedido', required=True, copy=False, readonly=True, default='Nuevo')
    catalog_id = fields.Many2one('digital.catalog', string='Catálogo', required=True, ondelete='cascade')
    partner_name = fields.Char(string='Nombre del cliente', required=True)
    partner_phone = fields.Char(string='Teléfono', required=True)
    partner_email = fields.Char(string='Correo electrónico')
    delivery_type = fields.Selection([('pickup', 'Recoger en tienda'), ('delivery', 'Entrega a domicilio')], string='Tipo de entrega', default='pickup', required=True)
    delivery_address = fields.Text(string='Dirección de entrega')
    notes = fields.Text(string='Notas')
    line_ids = fields.One2many('digital.catalog.order.line', 'order_id', string='Líneas del pedido')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('converted', 'Convertido a cotización'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Cotización de venta', readonly=True)
    total_amount = fields.Float(string='Total', compute='_compute_total_amount', store=True)
    company_id = fields.Many2one('res.company', string='Compañía', related='catalog_id.company_id', store=True, readonly=True)

    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = sum(order.line_ids.mapped('subtotal'))

    @api.model
    def create(self, vals):
        if vals.get('name') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'digital.catalog.order'
            ) or 'New'

        return super().create(vals)

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError('You cannot confirm an order without products.')

            if order.total_amount < order.catalog_id.minimum_order_amount:
                raise UserError('The order does not meet the minimum amount.')

            order.state = 'confirmed'

    def action_cancel(self):
        for order in self:
            order.state = 'cancelled'

    def action_reset_to_draft(self):
        for order in self:
            order.state = 'draft'

    def action_convert_to_sale_order(self):
        for order in self:
            if not order.line_ids:
                raise UserError('You cannot create a quotation without products.')

            if order.sale_order_id:
                raise UserError('This order already has a quotation.')

            partner = order._get_or_create_partner()

            sale_order = self.env['sale.order'].create({
                'partner_id': partner.id,
                'origin': order.name,
                'company_id': order.company_id.id,
                'note': order.notes or '',
                'order_line': [
                    (0, 0, {
                        'product_id': line.product_id.product_variant_id.id,
                        'product_uom_qty': line.quantity,
                        'price_unit': line.price_unit,
                    })
                    for line in order.line_ids
                ]
            })

            order.sale_order_id = sale_order.id
            order.state = 'converted'

        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
        }

    def _get_or_create_partner(self):
        self.ensure_one()

        partner = self.env['res.partner'].search([
            ('phone', '=', self.partner_phone)
        ], limit=1)

        if partner:
            return partner

        return self.env['res.partner'].create({
            'name': self.partner_name,
            'phone': self.partner_phone,
            'email': self.partner_email,
            'street': self.delivery_address if self.delivery_type == 'delivery' else False,
        })