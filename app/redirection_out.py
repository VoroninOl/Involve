from app.functions import generate_sign, generate_url, generate_list_by_alphabet
from flask import url_for, flash, redirect, render_template
from app.forms import PaymentForm
from app.config import *
import logging
import requests
import json

logging.basicConfig(filename='app/logs.log', level=logging.INFO,
                    format='%(levelname)s:%(message)s')


class PaymentRedirection:
    """Class to create object that can return redirection to another service
    Params:
        amount: str
            amount of money to pay
        currency: str
            code of currency
        shop_order_id: str
            id of order on shop side
        description: str
            description of product
        date: datetime.datetime
            date and time of order's creation"""

    def __init__(self, amount, currency, shop_order_id, description, date):
        """Constructor"""
        self.amount = amount
        self.currency = currency
        self.shop_order_id = shop_order_id
        self.description = description
        self.date = date

    def get_redirection(self):
        """Method to return redirection by currency code"""
        redirect_params = {
            'amount': self.amount,
            'currency': self.currency,
            'shop_order_id': self.shop_order_id,
            'description': self.description,
            'date': self.date}
        # If EUR
        if self.currency == code_eur:
            return redirect_to_pay(**redirect_params)
        # If USD
        elif self.currency == code_dol:
            return redirect_to_bill(**redirect_params)
        # If RUB
        elif self.currency == code_rub:
            return redirect_to_invoice(**redirect_params)


def redirect_to_pay(amount, currency, shop_order_id, description, date):
    """Function to redirect for protocol 'pay'
    Params:
        amount: str
            amount of money to pay
        currency: str
            code of currency
        shop_order_id: str
            id of order on shop side
        description: str
            description of product
        date: datetime.datetime
            date and time of order's creation"""

    params_dict = {
        'amount': amount,
        'currency': currency,
        'shop_id': shop_id,
        'shop_order_id': shop_order_id,
    }
    params_list = generate_list_by_alphabet(params_dict)
    sign = generate_sign(params_list)
    data = {
        'amount': amount,
        'currency': currency,
        'shop_id': shop_id,
        'sign': sign,
        'shop_order_id': shop_order_id,
        'description': description
    }
    logging.info('Order #{} created | Currency - {} | Amount - {} | Description - {} | Data - {}'
                 .format(shop_order_id, currency,
                         amount, description, date))
    url = generate_url(url_pay, data)
    return redirect(url)


def redirect_to_bill(amount, currency, shop_order_id, description, date):
    """Function to redirect for protocol 'bill'
    Params:
        amount: str
            amount of money to pay
        currency: str
            code of currency
        shop_order_id: str
            id of order on shop side
        description: str
            description of product
        date: datetime.datetime
            date and time of order's creation"""
    # !!!
    # That service messaged that you need to use that order
    # !!!
    params_list = [currency, amount, currency, shop_id, shop_order_id]
    sign = generate_sign(params_list)
    data = {
        "description": description,
        "payer_currency": currency,
        "shop_amount": amount,
        "shop_currency": currency,
        "shop_id": shop_id,
        "shop_order_id": shop_order_id,
        "sign": sign
    }

    # Sending request to another service to create bill
    r = requests.post(url_bill, json=data)
    answer = json.loads(r.text)
    if answer['result'] is True:
        logging.info('Order #{} created | Currency - {} | Amount - {} | Description - {} | Data - {}'
                     .format(shop_order_id, currency, amount,
                             description, date))
        return redirect(answer['data']['url'])
    else:
        logging.info('Order #{} failed | Error in Bill | Message - {}'
                     .format(shop_order_id, answer['message']))
        return redirect(url_for('index'))


def redirect_to_invoice(amount, currency, shop_order_id, description, date):
    """Function to redirect for protocol 'invoice'
    Params:
        amount: str
            amount of money to pay
        currency: str
            code of currency
        shop_order_id: str
            id of order on shop side
        description: str
            description of product
        date: datetime.datetime
            date and time of order's creation"""
    params_dict = {
        'amount': amount,
        'currency': currency,
        'shop_id': shop_id,
        'payway': payway,
        'shop_order_id': shop_order_id,
    }
    params_list = generate_list_by_alphabet(params_dict)
    sign = generate_sign(params_list)
    data = {
        "currency": currency,
        "amount": amount,
        'payway': payway,
        "shop_currency": currency,
        "shop_id": shop_id,
        "shop_order_id": shop_order_id,
        "sign": sign
    }

    # Sending request to another service to create invoice
    r = requests.post(url_invoice, json=data)
    answer = json.loads(r.text)
    if answer['result'] is True:
        logging.info('Order #{} created | Currency - {} | Amount - {} | Description - {} | Data - {}'
                     .format(shop_order_id, currency,
                             amount, description, date))
        url = generate_url(answer['data']['url'], answer['data'])
        return redirect(url)
    else:
        logging.info('Order #{} failed | Error in Bill | Message - {}'
                     .format(shop_order_id, answer['message']))
        flash('Order #{} failed | Error in Bill | Message - {}'
              .format(shop_order_id, answer['message']), category='danger')
        form = PaymentForm()
        return render_template('index.html', form=form)
