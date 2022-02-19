from app import app, db
from flask import render_template, flash
from app.models import Order
from app.forms import PaymentForm
from app.redirection_out import PaymentRedirection
import logging

logging.basicConfig(filename='app/logs.log', level=logging.INFO,
                    format='%(levelname)s:%(message)s')


@app.route('/',  methods=['GET', 'POST'])
def index():
    """Main route to render main page"""
    form = PaymentForm()
    if form.validate_on_submit():
        amount = str(form.amount.data)
        currency = form.currency.data
        order = Order(currency=currency, amount=amount)
        try:
            db.session.add(order)
            db.session.commit()
        except Exception as ex:
            logging.info('Order failed | Error in adding to database | Error - {}'.format(str(ex)))
            flash('Order failed | Error in adding to database | Error - {}'.format(str(ex)), category='danger')
            return render_template('index.html', form=form)

        redirection = PaymentRedirection(
            amount=amount, currency=currency, description=form.description.data,
            shop_order_id=order.shop_order_id, date=order.date
        )
        return redirection.get_redirection()

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash('There was an error | {}'.format(err_msg), category='danger')
    return render_template('index.html', form=form)
