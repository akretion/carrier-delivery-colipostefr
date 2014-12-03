# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: David BEAL
#    Copyright 2014 Akretion
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
    'name': 'Delivery Carrier ColiPoste, La Poste fr',
    'version': '0.3',
    'author': 'Akretion',
    'summary': 'Common features for Colissimo & So Colissimo transportation',
    'maintainer': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'partner_helper',
        # remove delivery_carrier_b2c dependency: carefull to
        # _complete_edi_lines() in deposit_slip.py
        'delivery_carrier_b2c',
        'document',
        'file_repository',
        'delivery_carrier_deposit',
    ],
    'description': """
Delivery Carrier ColiPoste
==========================

Description
-----------

This module is a common base to other modules which allow to generate labels
for your Delivery Orders with La Poste 'Colissimo' and 'So Colissimo (french).
It also generate edi file for la poste - colipostefr

Technical references
--------------------

`ColiPoste documentation`_

.. _documentation: https://www.coliposte.net

Contributors
------------

* David BEAL <david.beal@akretion.com>
* Benoit GUILLOT <benoit.guillot@akretion.com> (EDI part)
* Sébastien BEAU <sebastien.beau@akretion.com>

----


    """,
    'website': 'http://www.akretion.com/',
    'data': [
        'data/delivery.xml',
        'data/file_repository.xml',
        'config_view.xml',
        'stock_view.xml',
        'deposit_view.xml'
    ],
    'demo': [
        'demo/res.partner.csv',
        'demo/company.xml',
        'demo/product.xml',
    ],
    'external_dependencies': {
        'python': [
            'laposte_api',
            ],
    },
    'tests': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
