Stripe CLI (for webhook forwarding)
Install: https://stripe.com/docs/stripe-cli
Docker & Docker Compose


'Docker compose up' to begin
ADMIN ACCOUNT:
username = "admin_account"
email = "admin@bristolfoodnetwork.co.uk"
password = "admin123"

Customer or producers accounts will need to be created.

STRIPE API Guide
-Login to stripe dashboard
-go to developers -> API Keys
-copy your public and secret key into settings.py 

start docker,
run this command - stripe listen --forward-to localhost:8000/marketplace/stripe/webhook/
copy the webhook key and put it into the stripe_webhook_secret on settings.py.

MAKE SURE TO RUN stripe listen --forward-to localhost:8000/marketplace/stripe/webhook/ EVERY TIME YOU WISH TO SIMULATE STRIPE CHECKOUTS.

