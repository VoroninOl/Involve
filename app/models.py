
from app import db
from datetime import datetime


class Order(db.Model):
    """Model for user
    Columns: shop_order_id, currency, amount, date"""
    shop_order_id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.shop_order_id

