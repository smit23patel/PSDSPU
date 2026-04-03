# Flipkart Clone

A full-stack Flask e-commerce application modelled on Flipkart, with a complete backend and templated frontend.

## Features

- **User Auth** — Register / Login / Logout with hashed passwords (Werkzeug)
- **Product Catalog** — 8 seeded products across 4 categories; discount & rating display
- **Product Detail Page** — Full specs, related products, Buy Now / Add to Cart
- **Shopping Cart** — Add, remove, increment/decrement quantity; live subtotal & delivery charge
- **Checkout** — Address form + payment selector; order placed in DB
- **Order History** — All past orders with line items and status
- **Search** — Full-text ILIKE search + category filter
- **Flash Messages** — Feedback on every action (success / error / info)
- **Cart Badge** — Live count in navbar injected via context processor
- **Responsive** — Mobile-friendly grid (4 → 2 → 1 column)

## Project Structure

```
flipkart/
├── app.py                  # Main Flask application (models + routes)
├── wsgi.py                 # Gunicorn / Vercel entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── vercel.json
├── .env.example
├── .gitignore
├── static/
│   └── style.css           # Flipkart-themed CSS (CSS variables, responsive)
├── templates/
│   ├── base.html           # Navbar, flash messages, footer
│   ├── index.html          # Homepage — categories, banner, product grid
│   ├── search.html         # Search results + category filter bar
│   ├── product.html        # Product detail + related products
│   ├── cart.html           # Cart with qty controls + price summary
│   ├── checkout.html       # Address form + payment options
│   ├── order_success.html  # Post-checkout confirmation
│   ├── orders.html         # Order history
│   ├── login.html          # Login (split-panel Flipkart style)
│   └── register.html       # Registration form
└── api/
    └── index.py            # Vercel serverless entry point
```

## Database Models

| Model       | Key Fields |
|-------------|-----------|
| User        | username, email, password (hashed), created_at |
| Category    | name, icon |
| Product     | name, price, original_price, image, rating, review_count, category_id, in_stock, description |
| Cart        | user_id, product_id, quantity |
| Order       | user_id, total, placed_at, status |
| OrderItem   | order_id, product_id, quantity, price_at_purchase |

## Local Development

```bash
# 1. Clone / unzip the project
# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set a strong SECRET_KEY

# 5. Run
python app.py
# Visit http://localhost:5000
```

The app auto-creates `instance/database.db` and seeds 8 products + 4 categories on first run.

## Docker

```bash
# Development
docker-compose up --build

# Production (with nginx reverse proxy)
docker-compose --profile production up --build
```

## Deploy to Vercel

```bash
vercel deploy
```

Vercel routes all traffic to `api/index.py` which re-exports the Flask `app` object.
Set `SECRET_KEY` and `DATABASE_URL` as environment variables in the Vercel dashboard.
> Note: SQLite is ephemeral on Vercel — use a hosted Postgres (e.g. Neon, Supabase) and set `DATABASE_URL=postgresql://...` for production.

## Environment Variables

| Variable       | Default                  | Description |
|----------------|--------------------------|-------------|
| `SECRET_KEY`   | `dev-secret-key-...`     | Flask session secret — **change in production** |
| `DATABASE_URL` | `sqlite:///database.db`  | SQLAlchemy connection string |
| `FLASK_ENV`    | `production`             | `development` enables debug mode |
| `HOST`         | `0.0.0.0`                | Bind address |
| `PORT`         | `5000`                   | Bind port |

## Security Notes

- Passwords are hashed with `werkzeug.security.generate_password_hash` (PBKDF2-SHA256)
- Change `SECRET_KEY` before any public deployment
- Use HTTPS in production (nginx config included)
- Switch to PostgreSQL for multi-worker / production deployments
