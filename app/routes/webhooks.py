from flask import Blueprint, request, jsonify, current_app
import stripe
from ..models import db, Company, CompanyPaymentProfile, Customer, CustomerPaymentProfile, Payment, CustomerPaymentMethod

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config['STRIPE_WEBHOOK_SECRET']
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    connected_account_id = event.get('account') 
    
    if event['type'] == 'customer.created':
        handle_customer_created(event['data']['object'], connected_account_id)
    
    elif event['type'] == 'checkout.session.completed':
        handle_checkout_completed(event['data']['object'], connected_account_id)

    elif event['type'] == 'invoice.paid':
        handle_invoice_paid(event['data']['object'], connected_account_id)

    elif event['type'] == 'payment_method.attached':
        print("Payment method attached", event['data'])
        handle_payment_method_attached(event['data']['object'])

    return jsonify({"status": "success"}), 200

def get_or_create_customer(stripe_customer_id, customer_email, stripe_account_id):
    if not customer_email:
        return None

    profile = CompanyPaymentProfile.query.filter_by(stripe_account_id=stripe_account_id).first()
    if not profile:
        return None

    if not stripe_customer_id:
        stripe.api_key = current_app.config['STRIPE_PRIVATE_KEY']
        stripe_kwargs = {"stripe_account": stripe_account_id} if stripe_account_id else {}
        new_stripe_customer = stripe.Customer.create(email=customer_email, **stripe_kwargs)
        stripe_customer_id = new_stripe_customer.id

    customer = Customer.query.filter_by(email=customer_email, company_id=profile.company_id).first()
    if not customer:
        customer = Customer(email=customer_email, company_id=profile.company_id)
        db.session.add(customer)
        db.session.flush()
        new_profile = CustomerPaymentProfile(customer_id=customer.id, stripe_customer_id=stripe_customer_id)
        db.session.add(new_profile)
        db.session.commit()
    return customer

def handle_customer_created(stripe_customer, stripe_account_id):
    get_or_create_customer(stripe_customer.get('id'), stripe_customer.get('email'), stripe_account_id)

def handle_payment_method_attached(payment_method):
    stripe_customer_id = payment_method.get('customer')
    if not stripe_customer_id:
        return

    profile = CustomerPaymentProfile.query.filter_by(stripe_customer_id=stripe_customer_id).first()
    if profile:
        existing = CustomerPaymentMethod.query.filter_by(stripe_payment_method_id=payment_method['id']).first()
        if not existing:
            # Handle different types (card vs link)
            method_type = payment_method.get('type')
            brand = "Link"
            last4 = "****"
            print("payment_method", payment_method)
            print("method_type", method_type)
            print("card", payment_method.get('card', {}))
            if method_type == 'card':
                card = payment_method.get('card', {})
                brand = card.get('brand')
                last4 = card.get('last4')
            elif method_type == 'link':
                brand = "Link (Stripe)"
                # Link doesn't always provide last4 digits for security

            new_method = CustomerPaymentMethod(
                customer_id=profile.customer_id,
                stripe_payment_method_id=payment_method['id'],
                brand=brand,
                last4=last4
            )
            db.session.add(new_method)
            db.session.commit()

def update_payment_status(stripe_id, pi_id=None):
    payment = Payment.query.filter((Payment.stripe_id == stripe_id) | (Payment.stripe_id == pi_id)).first()
    if payment:
        payment.status = 'succeeded'
        db.session.commit()

def handle_checkout_completed(session, stripe_account_id):
    customer_details = session.get('customer_details') or {}
    customer_email = customer_details.get('email') or session.get('customer_email')
    stripe_customer_id = session.get('customer')
    
    if customer_email:
        get_or_create_customer(stripe_customer_id, customer_email, stripe_account_id)

    update_payment_status(session.get('id'), session.get('payment_intent'))

def handle_invoice_paid(invoice, stripe_account_id):
    customer_email = invoice.get('customer_email')
    stripe_customer_id = invoice.get('customer')
    
    if customer_email:
        get_or_create_customer(stripe_customer_id, customer_email, stripe_account_id)

    update_payment_status(invoice.get('id'), invoice.get('payment_intent'))
