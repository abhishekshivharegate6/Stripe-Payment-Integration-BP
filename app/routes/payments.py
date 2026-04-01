from flask import Blueprint, request, jsonify, render_template, current_app, redirect
from ..services.stripe_service import StripeService
from ..models import db, Company, CompanyPaymentProfile, Customer, CustomerPaymentProfile, Payment

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/checkout', methods=['GET'])
def checkout():
    account_id = request.args.get('account_id')
    email = request.args.get('email')
    
    customer = None
    if email and account_id:
        # ROBUST: Find the customer in our DB first
        profile = CompanyPaymentProfile.query.filter_by(stripe_account_id=account_id).first()
        if profile:
            customer = Customer.query.filter_by(email=email, company_id=profile.company_id).first()

    session = StripeService.create_checkout_session(customer=customer, stripe_account_id=account_id)
    return redirect(session.url, code=303)

@payments_bp.route('/invoice')
def invoice():
    email = request.args.get('email', 'test@example.com')
    account_id = request.args.get('account_id')
    
    if not account_id:
        return "Company Account ID is required.", 400

    profile = CompanyPaymentProfile.query.filter_by(stripe_account_id=account_id).first()
    if not profile:
        return "Company not found.", 404
    
    company = profile.company

    # 1. ROBUST: Get or Create Customer in our DB first
    customer = Customer.query.filter_by(email=email, company_id=company.id).first()
    if not customer:
        customer = Customer(email=email, company_id=company.id)
        db.session.add(customer)
        db.session.commit()

    # 2. Call Service with the DB Object
    stripe_invoice, stripe_customer_id = StripeService.create_invoice(customer, stripe_account_id=account_id)

    # 3. ROBUST: Ensure Stripe ID is saved in our DB if it was newly created
    if not customer.payment_profile:
        cust_profile = CustomerPaymentProfile(customer_id=customer.id, stripe_customer_id=stripe_customer_id)
        db.session.add(cust_profile)

    # 4. Record Payment
    new_payment = Payment(
        company_id=company.id, customer_id=customer.id, amount=stripe_invoice.amount_due,
        currency=stripe_invoice.currency, stripe_id=stripe_invoice.id, status='pending'
    )
    db.session.add(new_payment)
    db.session.commit()

    return redirect(stripe_invoice.hosted_invoice_url)

@payments_bp.route('/custom-payment')
def custom_payment():
    return render_template('payment.html', public_key=current_app.config['STRIPE_PUBLIC_KEY'])

@payments_bp.route('/create-payment-intent', methods=['POST'])
def handle_payment_intent():
    data = request.get_json()
    amount = data.get('amount', 2000)
    account_id = data.get('account_id')
    intent = StripeService.create_payment_intent(amount, stripe_account_id=account_id)
    return jsonify({'clientSecret': intent.client_secret})
