#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To know which keys to send to this library read these lists :
- required fields
- fields

in __init__ method for company information
and in manage_required_and_default_field method
"""

from mako.template import Template
from datetime import datetime

DEMO = True
#TODO pass the template as an argument
ENCODING = 'cp1252'
ERROR_BEHAVIOR = 'backslashreplace'
#TODO add a Exception error class
REQUIRED_FIELDS_ALERT = " /!\ !!! needs a valid value HERE !!! /!\ "


ProductLogo = {
    '6A': 'DOMI',
    '6C': 'DOMI',
    '6K': 'RENDEZ',
    '6J': 'CITY',
    '6H': 'BPOSTE',
    '6M': 'COMM',
}


class InvalidSequence(Exception):
    """ Invalid code sequence """


class InvalidZipCode(Exception):
    """ Invalid zip code """


class InvalidWeight(Exception):
    """ Invalid weight """


class InvalidDate(Exception):
    """ Invalid format for date """


class InvalidCodeLabel(Exception):
    """ Invalid code for shipping label """


class InvalidMissingField(Exception):
    """ Invalid missing Field """


class Label(object):

    def __init__(self, data, code):
        if not code in ["6", "6MA"]:
            raise InvalidCodeLabel('The code for the label must be 6 or 6MA')
        self.code = code
        self.data = data


class AbstractColissimo(object):

    def _build_control_key(self, key):
        #remove space
        key = key.replace(' ', '')
        # reverse string order
        key = key[::-1]
        pair, odd = [], []
        sum_pair, sum_odd = 0, 0
        my_count = 0
        for arg in key:
            my_count += 1
            if my_count % 2 == 0:
                pair.append(arg)
            else:
                odd.append(arg)

        for number in odd:
            sum_odd += int(number)
        for number in pair:
            sum_pair += int(number)

        my_sum = sum_odd * 3 + sum_pair
        result = (my_sum // 10 + 1) * 10 - my_sum
        if result == 10:
            result = 0
        return str(result)

    def get_cab_suivi(self, delivery):
        control_key = self._build_control_key(delivery['sequence'])
        return "%s %s %s"%(delivery['product_code'],
                           delivery['sequence'],
                           control_key)

    def get_cab_prise_en_charge(self, delivery, company, dropoff_site, label):
        prod_code = delivery['product_code']
        if label.code == '6MA':
            zip_code = '91500'
        elif prod_code in ['6J', '6H', '6M']:
            zip_code = dropoff_site['zip']
        else:
            zip_code = delivery['address']['zip'] #TODO FIXME wrong for dropoffsite
        barcode = (
            delivery['product_code']
            + '1 '
            + zip_code
            + ' '
            + company['account']
            + " %04d "%(delivery['weight'] * 100)
            + "00" #TODO support insurance
            + "%d"%delivery['non_machinable']
            + "0"
            + delivery['suivi_barcode'][12]
        )
        barcode += self._build_control_key(barcode[10:])
        return barcode


class Colissimo(AbstractColissimo):

    def __init__(self, company):
        required_fields = [
            'name',
            'street',
            'street2',
            'zip',
            'city',
            'account',
            'center_support_city',
        ]
        fields = [
            'phone',
            'account_chargeur',
        ]
        fields.extend(required_fields)
        self.check_required_and_set_default(fields, company, required_fields)
        self.company = company

    def _validate_data(self, delivery, dropoff_site):
        #TODO validate also the dropsite zip
        if len(delivery['address']['zip']) != 5:
            raise InvalidZipCode("Invalid zip code %s for France" % zip_code)

        if delivery['weight'] > 30:
            raise InvalidWeight("Invalid weight intead %s is superior to 30Kg"
                                % weight)

        if type(delivery['sequence']) not in [unicode, str]:
            raise InvalidSequence("The sequence must be an str or an unicode")
        if len(delivery['sequence']) != 10:
            raise InvalidSequence("The sequence len must be 10 instead of %s"
                                  %len(delivery['sequence']))
        if not delivery['sequence'].isdigit():
            raise InvalidSequence("Only digit char are authoried for"
                                  " the sequence")
        try:
            datetime.strptime(delivery['date'], '%d/%m/%Y')
        except ValueError:
            raise InvalidDate('The date must be at the format %d/%m/%Y')

    def get_label(self, label, delivery, dropoff_site):

        self._validate_data(delivery, dropoff_site)

        product_code = delivery['product_code']
        self.manage_required_and_default_field(delivery, dropoff_site)

        # direct key values
        kwargs = {'product_code': product_code, 'livraison_hors_domicile': ''}
        if product_code == '6J':
            if self.company['account_chargeur'] == '':
                kwargs['account_chargeur'] = REQUIRED_FIELDS_ALERT
            else:
                kwargs['account_chargeur'] = self.company['account_chargeur']


        # image 'France métropolitaine remise ...'
        if product_code == '6A':
            # sans signature
            kwargs['signature'] = 'SIGNS'
        else:
            # avec signature
            kwargs['signature'] = 'SIGNA'


        if product_code not in ['6A', '6C', '6K']:
            # produit colis 'mon domicile'
            kwargs['livraison_hors_domicile'] = delivery['address']['name'] + '\n\&'
        kwargs['logo'] = ProductLogo[product_code]

        delivery['suivi_barcode'] = self.get_cab_suivi(delivery)
        delivery['prise_en_charge_barcode'] = \
            self.get_cab_prise_en_charge(delivery, self.company, dropoff_site, label)

        if label.code == '6MA':
            kwargs['routage_barcode'] = self.routage_barcode(delivery, dropoff_site)
            kwargs['routage_barcode_full'] = kwargs['routage_barcode'].replace(' ','')
        else:
            # relative positionning element
            kwargs['vertical_text_box_width'] = 170
            kwargs['vertical_text_box_height'] = 290
            kwargs['vertical_text_pos_Y_suffix'] = 50
            if product_code in ['6H', '6M']:
                kwargs['vertical_text_pos_X'] = 560
                kwargs['vertical_text_pos_Y'] = 360
            elif product_code == '6J':
                kwargs['vertical_text_pos_X'] = 480
                kwargs['vertical_text_pos_Y'] = 570
            elif product_code in ['6A', '6C', '6K']:
                kwargs['vertical_text_pos_X'] = 590
                kwargs['vertical_text_pos_Y'] = 570
                kwargs['vertical_text_box_width'] = 140
                kwargs['vertical_text_pos_Y_suffix'] = 10

        zpl = Template(label.data).render(c=self.company, d=delivery, ds=dropoff_site, **kwargs)
        content = zpl.encode(encoding=ENCODING, errors=ERROR_BEHAVIOR)
        return {
            "zpl": content,
            "cab_suivi": delivery['suivi_barcode'],
            "cab_prise_en_charge": delivery['prise_en_charge_barcode'],
            "routage_barcode": kwargs.get('routage_barcode'),
        }

    #TODO FIXME should raise an error when fields are required
    #Also find a better way for empty fields
    def manage_required_and_default_field(self, delivery, dropoff_site):
        # delivery['address']
        required_fields = ['street', 'zip', 'city']
        fields = ['street2', 'street3', 'street4', 'door_code', 'door_code2', 'intercom', 'mobile', 'phone']
        fields.extend(required_fields)
        self.check_required_and_set_default(fields, delivery['address'], required_fields)

        # delivery
        required_fields = ['custom_shipping_ref', 'date', 'weight', 'sequence']
        fields = ['street2', 'street3', 'street4', 'phone', 'non_mecanisable']
        fields.extend(required_fields)
        self.check_required_and_set_default(fields, delivery, required_fields)

        if delivery['product_code'] in ['6M', '6J', '6H']:
            # dropoff_site
            required_fields = ['street', 'zip', 'city']
            fields = ['street2', 'street3', 'phone', 'name']
            fields.extend(required_fields)
            self.check_required_and_set_default(fields, dropoff_site, required_fields)

        return True

    def check_required_and_set_default(self, fields, dicto, required_fields):
        for field in fields:
            if field not in dicto or dicto[field] == False:
                if field in required_fields:
                    raise InvalidMissingField("Required field '%s' is missing"
                                %field)
                else:
                    dicto[field] = ''
        return True

    def routage_barcode(self, delivery, dropoff_site):
        zip = dropoff_site['zip'].zfill(7)
        suivi_barcode = delivery['suivi_barcode'].replace(' ','')
        barcode = '%' + zip[:4] + ' ' + zip[4:] + '6 ' + suivi_barcode[1:5] + ' '
        barcode += suivi_barcode[5:9] + ' ' + suivi_barcode[9:13] + ' 0849 250'

        openbar_var = barcode + self.routage_get_ctrl_key(barcode.replace(' ',''))
        return openbar_var

    def routage_get_ctrl_key(self, barcode):
        CAR = [str(x) for x in range(0,10)]
        string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        CAR.extend([x for x in string])
        CS, MOD = 36, 36
        #First char '%' is not take account
        for i in barcode[1:]:
            Y = CAR.index(i)
            CS += Y
            if CS > MOD:
                CS -= MOD
            CS *= 2
            if CS > MOD:
                CS = CS - MOD - 1

            #print i, Y
        CS = MOD + 1 - CS
        if CS == MOD:
            CS = 0
        return CAR[CS]
