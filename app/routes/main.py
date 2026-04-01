from flask import Blueprint, render_template, request, url_for, redirect
from ..models import db, Company, CompanyPaymentProfile

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def hello_world():
    return render_template('index.html')

@main_bp.route('/success')
def success():
    account_id = request.args.get('account_id')
    email = request.args.get('email') 
    account_type = request.args.get('type', 'standard')
    is_already_onboarded = request.args.get('already_onboarded') == 'true'
    
    if email and account_id and not is_already_onboarded:
        company = Company.query.filter_by(email=email).first()
        if not company:
            company = Company(email=email)
            db.session.add(company)
            db.session.flush()
        new_profile = CompanyPaymentProfile(
            company_id=company.id, stripe_account_id=account_id,
            account_type=account_type, onboarding_completed=True
        )
        db.session.add(new_profile)
        db.session.commit()

    msg = 'Welcome back!' if is_already_onboarded else 'Congratulations!'
    return f'''
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: #6366f1;">{msg}</h1>
            <p>Account ID: {account_id}</p>
            <a href="/">← Back Home</a>
        </div>
    '''

@main_bp.route('/cancel')
def cancel():
    return 'Action cancelled! <a href="/">Back Home</a>'
