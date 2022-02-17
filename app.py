from flask import Flask, render_template
from flask import redirect, request
from flask_sqlalchemy import SQLAlchemy
import json
import requests
from datetime import datetime
import logging
from pyfiles.functions import generate_sign, generate_url, is_digit
from pyfiles.config import shop_id, payway


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(levelname)s:%(message)s')

class Order(db.Model):
    """Model for user
    Columns: shop_order_id, currency, amount, date"""
    shop_order_id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.shop_order_id


@app.route('/',  methods=['GET', 'POST'])
def index():
    """Route to render main page"""
    if request.method == 'POST':
        amount = request.form['amount']
        currency = request.form['currency']
        description = request.form['description']

        if not is_digit(amount):
            logging.info('Order failed | Invalid value of amount')
            return redirect('/')
        order = Order(currency=currency, amount=amount)
        try:
            db.session.add(order)
            db.session.commit()
        except Exception as ex:
            logging.info('Order failed | Error in adding to database | Error - {}'.format(str(ex)))
            return redirect('/')
        # If EUR
        if currency == '978':
            # Alphabet order
            params_list = [amount, currency, shop_id, order.shop_order_id]
            sign = generate_sign(params_list)
            data = {
                'amount': amount,
                'currency': currency,
                'shop_id': shop_id,
                'sign': sign,
                'shop_order_id': order.shop_order_id,
                'description': description
            }
            logging.info('Order #{} created | Currency - {} | Amount - {} | Description - {} | Data - {}'
                         .format(order.shop_order_id, currency, amount, description, order.date))
            url = generate_url('https://pay.piastrix.com/ru/pay', data)
            return redirect(url)
        # If USD
        elif currency == '840':
            # Service messaged that you need to use that order
            params_list = [currency, amount , currency, shop_id, order.shop_order_id]
            sign = generate_sign(params_list)
            data = {
                "description": description,
                "payer_currency": currency,
                "shop_amount": amount,
                "shop_currency": currency,
                "shop_id": shop_id,
                "shop_order_id": order.shop_order_id,
                "sign": sign
            }
            r = requests.post('https://core.piastrix.com/bill/create', json=data)
            answer = json.loads(r.text)
            if answer['result'] is True:
                logging.info('Order #{} created | Currency - {} | Amount - {} | Description - {} | Data - {}'
                             .format(order.shop_order_id, currency, amount, description, order.date))
                return redirect(answer['data']['url'])
            else:
                logging.info('Order #{} failed | Error in Bill | Message - {}'
                             .format(order.shop_order_id, answer['message']))
                return redirect('/')
        # If RUB
        elif currency == '643':
            # Alphabet order
            params_list = [amount, currency, payway, shop_id, order.shop_order_id]
            sign = generate_sign(params_list)
            data = {
                "currency": currency,
                "amount": amount,
                'payway': payway,
                "shop_currency": currency,
                "shop_id": shop_id,
                "shop_order_id": order.shop_order_id,
                "sign": sign
            }
            r = requests.post('https://core.piastrix.com/invoice/create', json=data)
            answer = json.loads(r.text)
            if answer['result'] is True:
                logging.info('Order #{} created | Currency - {} | Amount - {} | Description - {} | Data - {}'
                             .format(order.shop_order_id, currency, amount, description, order.date))
                # return redirect(answer['data']['url'])
                url = generate_url('https://payeer.com/api/merchant/process.php', answer['data'])
                return redirect(url)
            else:
                logging.info('Order #{} failed | Error in Bill | Message - {}'
                             .format(order.shop_order_id, answer['message']))
                return redirect('/')
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(port=80)
