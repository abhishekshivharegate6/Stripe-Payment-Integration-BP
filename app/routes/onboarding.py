from flask import Blueprint, request, redirect, jsonify, url_for
from ..services.stripe_service import StripeService
from ..models import db, Company, CompanyPaymentProfile
import stripe

onboarding_bp = Blueprint('onboarding', __name__)

@onboarding_bp.route('/onboard')
def onboard():
    email = request.args.get('email')
    account_type = request.args.get('account_type', 'standard')
    if not email:
        return "Company email is required.", 400

    company = Company.query.filter_by(email=email).first()
    existing_id = company.payment_profile.stripe_account_id if company and company.payment_profile else None
    
    link, already_onboarded = StripeService.onboard_company(
        account_type=account_type, existing_account_id=existing_id, email=email
    )
    
    if already_onboarded:
        return redirect(url_for('main.success', account_id=existing_id, already_onboarded='true'))
    
    return redirect(link.url)

@onboarding_bp.route('/dashboard')
def dashboard():
    account_id = request.args.get('account_id')
    try:
        login_link = stripe.Account.create_login_link(account_id)
        return redirect(login_link.url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@onboarding_bp.route('/disconnect', methods=['POST'])
def handle_disconnect():
    account_id = request.form.get('account_id')
    profile = CompanyPaymentProfile.query.filter_by(stripe_account_id=account_id).first()
    if profile:
        company = profile.company
        db.session.delete(profile)
        db.session.delete(company)
        db.session.commit()
    
    StripeService.deauthorize_account(account_id)
    return jsonify({"message": "Disconnected"})
