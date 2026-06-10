from odoo import models, fields, api
from odoo.exceptions import UserError
import re

class DigitalCatalog(models.Model):
    _name = 'digital.catalog'
    _description = 'Catálogo digital'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre del catálogo", required=True, tracking=True)
    slug = fields.Char(string="Slug público", required=True, copy=False, tracking=True)
    active = fields.Boolean(string="Activo", default=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company, required=True)
    product_ids = fields.Many2many('product.template', string='Productos')
    show_prices = fields.Boolean(string='Mostrar precios', default=True)
    show_stock = fields.Boolean(string='Mostrar stock', default=False)
    allow_orders = fields.Boolean(string='Permitir pedidos', default=True)
    minimum_order_amount = fields.Float(string='Monto mínimo de pedido', default=0.0)
    whatsapp_number = fields.Char(string='Número de WhatsApp')
    primary_color = fields.Char(string='Color principal', default='#111827')
    description = fields.Text(string='Descripción')
    public_url = fields.Char(string='URL pública', compute='_compute_public_url')
    order_count = fields.Integer(string='Pedidos', compute='_compute_order_count')

    _sql_constraints = [('digital_catalog_slug_unique', 'unique(slug)', 'The public slug must be unique.')]

    @api.depends('slug')
    def _compute_public_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for catalog in self:
            if catalog.slug:
                catalog.public_url = f'{base_url}/catalogo/{catalog.slug}'
            else:
                catalog.public_url = False

    def _compute_order_count(self):
        for catalog in self:
            catalog.order_count = self.env['digital.catalog.order'].search_count([
                ('catalog_id', '=', catalog.id)
            ])

    @api.constrains('slug')
    def _check_slug(self):
        pattern = re.compile(r'^[a-z0-9-]+$')

        for catalog in self:
            if catalog.slug and not pattern.match(catalog.slug):
                raise ValidationError(
                    'The slug can only contain lowercase letters, numbers, and hyphens.'
                )

    @api.model
    def create(self, vals):
        if vals.get('name') and not vals.get('slug'):
            vals['slug'] = self._generate_slug(vals['name'])

        return super().create(vals)

    def write(self, vals):
        if vals.get('slug'):
            vals['slug'] = self._clean_slug(vals['slug'])

        return super().write(vals)

    def _generate_slug(self, name):
        slug = self._clean_slug(name)
        original_slug = slug
        counter = 1

        while self.search_count([('slug', '=', slug)]):
            slug = f'{original_slug}-{counter}'
            counter += 1

        return slug

    def _clean_slug(self, text):
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'\s+', '-', text)
        text = re.sub(r'-+', '-', text)
        return text.strip('-')

    def action_view_orders(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Catalog Orders',
            'res_model': 'digital.catalog.order',
            'view_mode': 'tree,form',
            'domain': [('catalog_id', '=', self.id)],
            'context': {
                'default_catalog_id': self.id
            }
        }