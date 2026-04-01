import stripe
import os
from flask import request, url_for, current_app
from urllib.parse import urlencode

class StripeService:
    @staticmethod
    def get_api_key():
        stripe.api_key = current_app.config['STRIPE_PRIVATE_KEY']
        return stripe.api_key

    @staticmethod
    def create_checkout_session(customer=None, stripe_account_id=None):
        StripeService.get_api_key()
        stripe_kwargs = {"stripe_account": stripe_account_id} if stripe_account_id else {}
        
        kwargs = {
            "line_items": [{"price_data": {"currency": "usd", "product_data": {"name": "T-shirt"}, "unit_amount": 2000}, "quantity": 1}],
            "mode": 'payment',
            "success_url": request.host_url + 'success',
            "cancel_url": request.host_url + 'cancel',
            # Enable saving payment methods
            "payment_intent_data": {
                "setup_future_usage": "off_session",
            }
        }

        if customer and customer.payment_profile:
            kwargs["customer"] = customer.payment_profile.stripe_customer_id
        elif customer:
            kwargs["customer_email"] = customer.email
            kwargs["customer_creation"] = "always"
        else:
            kwargs["customer_creation"] = "always"

        if stripe_account_id:
            return stripe.checkout.Session.create(**kwargs, stripe_account=stripe_account_id)
        return stripe.checkout.Session.create(**kwargs)

    @staticmethod
    def create_invoice(customer, stripe_account_id=None):
        StripeService.get_api_key()
        stripe_kwargs = {"stripe_account": stripe_account_id} if stripe_account_id else {}
        
        if customer.payment_profile:
            stripe_customer_id = customer.payment_profile.stripe_customer_id
        else:
            stripe_customer = stripe.Customer.create(email=customer.email, **stripe_kwargs)
            stripe_customer_id = stripe_customer.id

        invoice = stripe.Invoice.create(
            customer=stripe_customer_id, collection_method="send_invoice", days_until_due=7, currency="usd",
            pending_invoice_items_behavior="exclude", **stripe_kwargs
        )
        stripe.InvoiceItem.create(
            customer=stripe_customer_id, invoice=invoice.id, amount=250000, currency="usd", 
            description="Dichlore Shock", **stripe_kwargs
        )
        return stripe.Invoice.finalize_invoice(invoice.id, **stripe_kwargs), stripe_customer_id

    @staticmethod
    def get_payment_methods(stripe_customer_id, stripe_account_id=None):
        StripeService.get_api_key()
        stripe_kwargs = {"stripe_account": stripe_account_id} if stripe_account_id else {}
        return stripe.PaymentMethod.list(
            customer=stripe_customer_id,
            type="card",
            **stripe_kwargs
        )

    @staticmethod
    def onboard_company(account_type="standard", existing_account_id=None, email=None):
        StripeService.get_api_key()
        if existing_account_id:
            account = stripe.Account.retrieve(existing_account_id)
            if account.details_submitted:
                return None, True

        account = stripe.Account.retrieve(existing_account_id) if existing_account_id else stripe.Account.create(
            type=account_type, capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True}}
        )
        
        params = {"account_id": account.id}
        if email: params.update({"email": email, "type": account_type})
        
        base_url = request.host_url.rstrip('/')
        return stripe.AccountLink.create(
            account=account.id, refresh_url=f"{base_url}/onboard?{urlencode(params)}",
            return_url=f"{base_url}/success?{urlencode(params)}", type="account_onboarding"
        ), False

    @staticmethod
    def deauthorize_account(stripe_account_id):
        StripeService.get_api_key()
        return stripe.OAuth.deauthorize(
            client_id=current_app.config['STRIPE_CLIENT_ID'],
            stripe_user_id=stripe_account_id,
        )

    @staticmethod
    def create_payment_intent(amount, currency="usd", stripe_account_id=None):
        StripeService.get_api_key()
        stripe_kwargs = {"stripe_account": stripe_account_id} if stripe_account_id else {}
        return stripe.PaymentIntent.create(
            amount=amount, currency=currency, automatic_payment_methods={"enabled": True}, **stripe_kwargs
        )
