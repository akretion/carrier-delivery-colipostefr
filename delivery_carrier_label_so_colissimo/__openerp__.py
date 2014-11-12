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
    'name': 'Delivery Carrier Label So Colissimo',
    'version': '0.3',
    'author': 'Akretion',
    'summary': "Direct label printing for ColiPoste So Colissimo carrier",
    'maintainer': 'Akretion',
    'category': 'Warehouse',
    'depends': [
        'delivery_carrier_colipostefr',
        'delivery_dropoff_site',
    ],
    'description': """
Carrier label So Colissimo
==========================

Description
-----------

* Manage So Colissimo labels and reports generation
for 'ColisPoste - La Poste - FR'

* Add new delivery methods and zpl reports

So Colissimo specific :
~~~~~~~~~~~~~~~~~~~~~~~

* A2P : commerce de proximité
* CIT : Cityssimo

* CDI : Centre de distribution de la poste
* ACP : Agence Coliposte
* BPR : Bureau de poste

Settings
--------

  * Complete the 'File Repository' (Settings > File exchange > File repository)
    with your Ftp, Sftp or file system parameter
  * Complete the task 'Mise à jour des points relais' in this file repository
    with 'Folder', 'File Name' and 'Archive Folder'
  * Add a cron by click button 'add cron' in this task and modify
    the execution period as you need

TODO
----
So Colissimo Belgique



Contributors
------------

* David BEAL <david.beal@akretion.com>
* Sébastien BEAU <sebastien.beau@akretion.com>


    """,
    'website': 'http://www.akretion.com/',
    'data': [
        'data/delivery.xml',
        'data/sequence.xml',
        'config_view.xml',
        'partner_view.xml',
    ],
    'demo': [
        'demo/deposit_slip_demo.xml',
        'demo/partner.dropoff.site.csv',
        #TODO : to fix
        'demo/partner.dropoff.site.csv',
        'demo/stock.picking.csv',
        'demo/stock.move.csv',
    ],
    'tests': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
    'external_dependencies': {
        'Python': ['unicodecsv'],
    },
}
