# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Delivery Roulier Coliposte',
    'version': '0.3',
    'author': 'Akretion',
    'summary': "Direct label printing for ColiPoste International carrier",
    'maintainer': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'delivery_carrier_label_colissimo',
    ],
    'description': """



Contributors
------------

* David BEAL <david.beal@akretion.com>


    """,
    'website': 'http://www.akretion.com/',
    'data': [
        'data/delivery.xml',
    ],
    'tests': [],
    'demo': [
    ],
    'external_dependencies': {
        'python': [
            'roulier',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}