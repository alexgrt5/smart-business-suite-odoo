{
    'name': 'Catálogo Digital y Pedidos Públicos',
    'version': '1.0.0',
    'category': 'Sales',
    'summary': 'Catálogo digital con pedidos públicos y compartición mediante código QR.',
    'description': '''
Catálogo digital de productos con pedidos móviles para el público.

Los clientes pueden explorar productos y realizar pedidos sin necesidad de una plataforma de comercio electrónico completa.
    ''',
    'author': 'alexgrt1',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'sale',
        'stock',
        'website',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/digital_catalog_views.xml',
        'views/digital_catalog_order_views.xml',
        'views/menu_views.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'digital_catalog_orders/static/src/js/catalog_cart.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}