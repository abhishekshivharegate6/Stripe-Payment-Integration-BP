# Stripe Connect SaaS POC - ABHISHEK SHIVHARE

A professional, modular Flask-based SaaS infrastructure designed for multi-tenant payment processing using Stripe Connect. This platform allows multiple companies to onboard, manage customers, and collect payments directly.

## 🚀 Features

- **Multi-Tenant Onboarding**: Support for both **Standard** and **Express** Stripe accounts.
- **Robust ID-based Tracking**: Database-first architecture using internal IDs to prevent duplicate Stripe objects.
- **Automated Invoicing**: Generate finalized PDF and hosted invoices on behalf of connected accounts.
- **Custom Payment UI**: Integrated Stripe Elements for a branded, on-site checkout experience.
- **Real-time Webhooks**: Automated database synchronization for customers, payment methods, and payment statuses.
- **Modular Architecture**: Service-layer pattern with Blueprints for maximum maintainability.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.10+**
- **MySQL Server** (running on port 3306)
- **Stripe CLI** (for local webhook testing)
- **DBeaver** or MySQL Workbench (to view the database)

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd stripe-yeeld-poc
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration

Create a `.env` file in the root directory and add your credentials:

```env
# Stripe API Keys (from Dashboard > Developers > API keys)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_PRIVATE_KEY=sk_test_...

# Connect Client ID (from Dashboard > Settings > Connect > Settings)
STRIPE_CLIENT_ID=ca_...

# Webhook Secret (obtained from 'stripe listen' command)
STRIPE_WEBHOOK_SECRET=whsec_...

# MySQL Configuration
# Format: mysql+mysqlconnector://user:password@host/database_name
DATABASE_URL=mysql+mysqlconnector://root:yourpassword@localhost/stripe_poc
```

> **Note**: You must register `http://127.0.0.1:5000/callback` in your Stripe Dashboard under **Connect Settings > Redirect URIs**.

---

## 🗄️ Database Setup

1. **Create the MySQL Database:**
   ```sql
   CREATE DATABASE stripe_poc;
   ```

2. **Run Migrations:**
   ```bash
   flask db upgrade
   ```

---

## 🚦 Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Start the Stripe Webhook listener (in a separate terminal):**
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```

3. **Visit the app:**
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📂 Project Structure

```text
├── app/
│   ├── routes/          # Blueprints (main, onboarding, payments, webhooks)
│   ├── services/        # StripeService (Core SDK logic)
│   ├── templates/       # HTML UI (index, payment)
│   ├── models.py        # SQLAlchemy Models (Company, Customer, Payment)
│   └── __init__.py      # App Factory
├── migrations/          # Database version control
├── config.py            # App configuration
├── app.py               # Entry point
└── .env                 # Environment variables (Secrets)
```

---

## 🛠️ Usage Guide

### 1. Onboarding a Company
Enter a company email on the homepage. Choose **Standard** (if they have an existing account) or **Express** (to create a new one). This saves the company to your database automatically.

### 2. Processing Payments
Use the **Connect Account Tools** section. Enter the customer's email and the company's `account_id` to trigger a checkout session or invoice.

### 3. Saving Cards
When a customer pays via Checkout, the system automatically saves their payment method to the `customer_payment_methods` table via webhooks for future 1-click charges.
