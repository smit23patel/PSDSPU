from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---- MODELS ----

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(300))
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    original_price = db.Column(db.Integer)
    image = db.Column(db.String(300))
    rating = db.Column(db.Float, default=4.2)
    review_count = db.Column(db.Integer, default=1200)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    in_stock = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, default='')

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Integer, nullable=False)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Confirmed')
    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price_at_purchase = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product')


# ---- CONTEXT PROCESSOR ----

@app.context_processor
def inject_globals():
    count = 0
    if 'user' in session:
        count = Cart.query.filter_by(user_id=session['user']).count()
    return dict(cart_count=count, current_user=session.get('username'))


# ---- ROUTES ----

@app.route("/")
def home():
    products = Product.query.filter_by(in_stock=True).all()
    categories = Category.query.all()
    return render_template("index.html", products=products[:8], categories=categories)


@app.route("/register", methods=["GET", "POST"])
def register():
    if 'user' in session:
        return redirect("/")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not username or not password:
            flash("Username and password required.", "error")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")
        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return render_template("register.html")
        u = User(username=username, email=email or None)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect("/")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/")
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect("/")


@app.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()
    return render_template("product.html", product=product, related=related)


@app.route("/add/<int:id>")
def add_to_cart(id):
    if "user" not in session:
        flash("Please log in to add items.", "info")
        return redirect("/login")
    product = Product.query.get_or_404(id)
    existing = Cart.query.filter_by(user_id=session["user"], product_id=id).first()
    if existing:
        existing.quantity += 1
    else:
        db.session.add(Cart(user_id=session["user"], product_id=id))
    db.session.commit()
    flash(f'"{product.name[:40]}..." added to cart!', "success")
    return redirect(request.referrer or "/")


@app.route("/cart")
def cart():
    if "user" not in session:
        return redirect("/login")
    items = Cart.query.filter_by(user_id=session["user"]).all()
    cart_items, subtotal = [], 0
    for i in items:
        p = Product.query.get(i.product_id)
        if p:
            cart_items.append({'cart': i, 'product': p, 'total': p.price * i.quantity})
            subtotal += p.price * i.quantity
    delivery = 0 if subtotal >= 500 else 40
    return render_template("cart.html", cart_items=cart_items, subtotal=subtotal,
                           delivery=delivery, total=subtotal + delivery)


@app.route("/update_cart/<int:id>", methods=["POST"])
def update_cart(id):
    if "user" not in session:
        return redirect("/login")
    action = request.form.get("action")
    item = Cart.query.filter_by(user_id=session["user"], product_id=id).first()
    if item:
        if action == "increase":
            item.quantity += 1
        elif action == "decrease":
            item.quantity -= 1
            if item.quantity <= 0:
                db.session.delete(item)
        db.session.commit()
    return redirect("/cart")


@app.route("/remove/<int:id>")
def remove_from_cart(id):
    if "user" not in session:
        return redirect("/login")
    item = Cart.query.filter_by(user_id=session["user"], product_id=id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    flash("Item removed.", "info")
    return redirect("/cart")


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user" not in session:
        return redirect("/login")
    items = Cart.query.filter_by(user_id=session["user"]).all()
    if not items:
        flash("Cart is empty.", "info")
        return redirect("/cart")
    if request.method == "POST":
        total = 0
        order = Order(user_id=session["user"], total=0)
        db.session.add(order)
        db.session.flush()
        for i in items:
            p = Product.query.get(i.product_id)
            if p:
                total += p.price * i.quantity
                db.session.add(OrderItem(order_id=order.id, product_id=p.id,
                                         quantity=i.quantity, price_at_purchase=p.price))
            db.session.delete(i)
        order.total = total
        db.session.commit()
        return render_template("order_success.html", order=order)
    cart_items, subtotal = [], 0
    for i in items:
        p = Product.query.get(i.product_id)
        if p:
            cart_items.append({'cart': i, 'product': p})
            subtotal += p.price * i.quantity
    return render_template("checkout.html", cart_items=cart_items, subtotal=subtotal)


@app.route("/orders")
def orders():
    if "user" not in session:
        return redirect("/login")
    user_orders = Order.query.filter_by(user_id=session["user"]).order_by(Order.placed_at.desc()).all()
    return render_template("orders.html", orders=user_orders)


@app.route("/search")
def search():
    query = request.args.get('q', '').strip()
    category_id = request.args.get('cat', None)
    qset = Product.query.filter_by(in_stock=True)
    if query:
        qset = qset.filter(Product.name.ilike(f'%{query}%'))
    if category_id:
        qset = qset.filter_by(category_id=category_id)
    categories = Category.query.all()
    return render_template("search.html", products=qset.all(),
                           search_query=query, categories=categories,
                           selected_category=category_id)


# ---- SEED ----

def seed_data():
    if Product.query.first():
        return
    cat_data = [
        ('Electronics', 'https://rukminim2.flixcart.com/flap/80/80/image/69c6589653afdb9a.png'),
        ('Fashion', 'https://rukminim2.flixcart.com/flap/80/80/image/0d75b34f7d8fbcb3.png'),
        ('Home', 'https://rukminim2.flixcart.com/flap/80/80/image/ab7e2b022a4587dd.jpg'),
        ('Appliances', 'https://rukminim2.flixcart.com/flap/80/80/image/0139228b2f7eb413.jpg'),
    ]
    cats = {}
    for name, icon in cat_data:
        c = Category(name=name, icon=icon)
        db.session.add(c)
        db.session.flush()
        cats[name] = c.id

    products = [
        Product(name="Apple iPhone 15 (Black, 128 GB)", price=72999, original_price=84900,
                image="https://images.unsplash.com/photo-1695048133142-1a20484aa0dc?auto=format&fit=crop&w=800&q=80",
                rating=4.6, review_count=42381, category_id=cats['Electronics'],
                description="Experience the A16 Bionic chip with a 48MP main camera."),
        Product(name="SAMSUNG Galaxy S23 Ultra 5G (256 GB)", price=104999, original_price=124999,
                image="https://images.unsplash.com/photo-1678911820864-e2c567c655d7?auto=format&fit=crop&w=800&q=80",
                rating=4.5, review_count=18920, category_id=cats['Electronics'],
                description="200MP camera, built-in S Pen, and powerful Snapdragon 8 Gen 2."),
        Product(name="SONY PlayStation 5 Console", price=54990, original_price=59990,
                image="https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=800&q=80",
                rating=4.8, review_count=8741, category_id=cats['Electronics'],
                description="Next-gen gaming with ultra-high speed SSD and 3D audio."),
        Product(name="MacBook Air M2 (8GB RAM, 256GB SSD)", price=99990, original_price=119990,
                image="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
                rating=4.7, review_count=12034, category_id=cats['Electronics'],
                description="Supercharged by M2, impossibly thin, fanless design."),
        Product(name="boAt Rockerz 450 Bluetooth Headphone", price=1299, original_price=3990,
                image="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
                rating=4.1, review_count=74312, category_id=cats['Electronics'],
                description="15-hour playtime, 40mm drivers, foldable design."),
        Product(name="Nike Air Max 270 Running Shoes", price=8995, original_price=12995,
                image="https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80",
                rating=4.3, review_count=9823, category_id=cats['Fashion'],
                description="Lightweight, breathable, with Air Max heel unit."),
        Product(name="Philips Air Fryer HD9200 (4.1 Litre)", price=4499, original_price=7995,
                image="https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=800&q=80",
                rating=4.4, review_count=31205, category_id=cats['Appliances'],
                description="Up to 90% less fat using Rapid Air Technology."),
        Product(name="Wooden 6-Seater Dining Table Set", price=18999, original_price=35000,
                image="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80",
                rating=4.0, review_count=2100, category_id=cats['Home'],
                description="Solid sheesham wood with 6 cushioned chairs."),
    ]
    db.session.add_all(products)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
