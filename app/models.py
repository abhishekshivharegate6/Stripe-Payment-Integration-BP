from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    payment_profile = db.relationship('CompanyPaymentProfile', backref='company', uselist=False, lazy=True)
    customers = db.relationship('Customer', backref='company', lazy=True)
    payments = db.relationship('Payment', backref='company', lazy=True)

class CompanyPaymentProfile(db.Model):
    __tablename__ = 'company_payment_profiles'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    stripe_account_id = db.Column(db.String(50), unique=True, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    onboarding_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    payment_profile = db.relationship('CustomerPaymentProfile', backref='customer', uselist=False, lazy=True)
    payment_methods = db.relationship('CustomerPaymentMethod', backref='customer', lazy=True)

class CustomerPaymentProfile(db.Model):
    __tablename__ = 'customer_payment_profiles'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    stripe_customer_id = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CustomerPaymentMethod(db.Model):
    __tablename__ = 'customer_payment_methods'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    stripe_payment_method_id = db.Column(db.String(100), unique=True, nullable=False)
    brand = db.Column(db.String(20)) # e.g., visa
    last4 = db.Column(db.String(4))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), default='usd')
    stripe_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
