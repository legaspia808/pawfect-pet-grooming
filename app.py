import os
from datetime import date, datetime
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
SERVICES = {
    "Bath & Brush": "₱450+",
    "Full Groom": "₱800+",
    "Puppy Intro": "₱500+",
    "Nail & Paw Care": "₱250+",
}
PET_TYPES = ["Dog", "Cat", "Other"]
STATUSES = ["Pending", "Confirmed", "In Grooming", "Ready for Pickup", "Completed", "Cancelled"]
APPOINTMENT_TIMES = [f"{hour:02d}:{minute:02d}" for hour in range(9, 18) for minute in (0, 30)]

# Database models

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    reservations = db.relationship("Reservation", backref="customer", cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="author", cascade="all, delete-orphan")


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pet_name = db.Column(db.String(80), nullable=False)
    pet_type = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(80), nullable=False)
    appointment_date = db.Column(db.String(10), nullable=False)
    appointment_time = db.Column(db.String(5), nullable=False)
    notes = db.Column(db.String(500), nullable=False, default="")
    status = db.Column(db.String(30), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pet_name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    message = db.Column(db.String(500), nullable=False)
    photo_filename = db.Column(db.String(255), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "local-development-key-change-before-deploy")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

    database_url = os.getenv("DATABASE_URL", "").strip()
    # Some hosting providers still present the older postgres:// scheme.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{BASE_DIR / 'pawfect.db'}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    def current_user():
        user_id = session.get("user_id")
        return db.session.get(User, user_id) if user_id else None

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if current_user() is None:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)
        return wrapped

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if user is None:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login", next=request.path))
            if user.role != "admin":
                abort(403)
            return view(*args, **kwargs)
        return wrapped

    app.jinja_env.globals.update(
        current_user=current_user,
        services=SERVICES,
        pet_types=PET_TYPES,
        statuses=STATUSES,
        appointment_times=APPOINTMENT_TIMES,
    )

    def safe_next(default_endpoint="dashboard"):
        next_path = request.args.get("next", "")
        if next_path.startswith("/") and not next_path.startswith("//"):
            return next_path
        return url_for(default_endpoint)

    def reservation_form_values(form):
        pet_name = form.get("pet_name", "").strip()
        pet_type = form.get("pet_type", "")
        service = form.get("service", "")
        appointment_date = form.get("appointment_date", "")
        appointment_time = form.get("appointment_time", "")
        notes = form.get("notes", "").strip()
        try:
            valid_date = date.fromisoformat(appointment_date) >= date.today()
        except ValueError:
            valid_date = False
        if not pet_name or len(pet_name) > 80:
            return None, "Enter your pet's name (80 characters or fewer)."
        if pet_type not in PET_TYPES:
            return None, "Choose a valid pet type."
        if service not in SERVICES:
            return None, "Choose a grooming service from the list."
        if not valid_date:
            return None, "Choose today or a future appointment date."
        if appointment_time not in APPOINTMENT_TIMES:
            return None, "Choose an appointment time between 9:00 AM and 5:30 PM."
        if len(notes) > 500:
            return None, "Notes must be 500 characters or fewer."
        return {
            "pet_name": pet_name,
            "pet_type": pet_type,
            "service": service,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "notes": notes,
        }, None

    @app.route("/")
    def home():
        reviews = Review.query.order_by(Review.created_at.desc()).limit(12).all()
        return render_template("index.html", reviews=reviews)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if not name or len(name) > 100:
                flash("Enter your name (100 characters or fewer).", "danger")
            elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                flash("Enter a valid email address.", "danger")
            elif User.query.filter_by(email=email).first():
                flash("That email is already registered. Please log in.", "danger")
            elif len(password) < 8:
                flash("Password must be at least 8 characters.", "danger")
            else:
                db.session.add(User(name=name, email=email, password_hash=generate_password_hash(password), role="customer"))
                db.session.commit()
                flash("Your account has been created. Please log in.", "success")
                return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter_by(email=email).first()
            if user is None or not check_password_hash(user.password_hash, password):
                flash("Invalid email or password.", "danger")
            else:
                session.clear()
                session["user_id"] = user.id
                flash(f"Welcome, {user.name}!", "success")
                if user.role == "admin":
                    return redirect(url_for("admin_dashboard"))
                return redirect(safe_next("dashboard"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("home"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        if user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        reservations = Reservation.query.filter_by(customer_id=user.id).order_by(Reservation.created_at.desc()).all()
        reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).all()
        return render_template("dashboard.html", reservations=reservations, reviews=reviews)

    @app.route("/reservation/new", methods=["GET", "POST"])
    @login_required
    def new_reservation():
        if request.method == "POST":
            values, error = reservation_form_values(request.form)
            if error:
                flash(error, "danger")
            else:
                reservation = Reservation(customer_id=current_user().id, **values)
                db.session.add(reservation)
                db.session.commit()
                flash("Reservation request submitted. Our team will confirm it soon.", "success")
                return redirect(url_for("dashboard"))
        return render_template("reservation_form.html", reservation=None, today=date.today().isoformat())

    @app.route("/reservation/<int:reservation_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_reservation(reservation_id):
        reservation = db.get_or_404(Reservation, reservation_id)
        user = current_user()
        if user.role != "admin" and reservation.customer_id != user.id:
            abort(403)
        if user.role != "admin" and reservation.status != "Pending":
            flash("Customers can edit only pending reservations. Contact the studio if you need a change.", "warning")
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            values, error = reservation_form_values(request.form)
            if error:
                flash(error, "danger")
            else:
                for key, value in values.items():
                    setattr(reservation, key, value)
                if user.role == "admin":
                    status = request.form.get("status", reservation.status)
                    if status in STATUSES:
                        reservation.status = status
                db.session.commit()
                flash("Reservation updated.", "success")
                return redirect(url_for("admin_dashboard" if user.role == "admin" else "dashboard"))
        return render_template("reservation_form.html", reservation=reservation, today=date.today().isoformat())

    @app.post("/reservation/<int:reservation_id>/delete")
    @login_required
    def delete_reservation(reservation_id):
        reservation = db.get_or_404(Reservation, reservation_id)
        user = current_user()
        if user.role != "admin" and reservation.customer_id != user.id:
            abort(403)
        if user.role != "admin" and reservation.status != "Pending":
            flash("Customers can delete only pending reservations.", "warning")
            return redirect(url_for("dashboard"))
        db.session.delete(reservation)
        db.session.commit()
        flash("Reservation deleted.", "success")
        return redirect(url_for("admin_dashboard" if user.role == "admin" else "dashboard"))

    @app.post("/review/new")
    @login_required
    def new_review():
        pet_name = request.form.get("pet_name", "").strip()
        message = request.form.get("message", "").strip()
        try:
            rating = int(request.form.get("rating", "5"))
        except ValueError:
            rating = 0
        if not pet_name or len(pet_name) > 80 or not message or len(message) > 500 or rating not in range(1, 6):
            flash("Enter your pet's name, a review (up to 500 characters), and a rating from 1 to 5.", "danger")
            return redirect(url_for("dashboard") + "#share-review")
        photo = request.files.get("photo")
        filename = ""
        if photo and photo.filename:
            cleaned = secure_filename(photo.filename)
            extension = cleaned.rsplit(".", 1)[-1].lower() if "." in cleaned else ""
            if extension not in ALLOWED_IMAGE_EXTENSIONS:
                flash("Photo must be JPG, JPEG, PNG, WEBP or GIF.", "danger")
                return redirect(url_for("dashboard") + "#share-review")
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{cleaned}"
            photo.save(UPLOAD_DIR / filename)
        db.session.add(Review(user_id=current_user().id, pet_name=pet_name, rating=rating, message=message, photo_filename=filename))
        db.session.commit()
        flash("Thank you for sharing your Pawfect review!", "success")
        return redirect(url_for("dashboard") + "#share-review")

    @app.post("/review/<int:review_id>/delete")
    @login_required
    def delete_review(review_id):
        review = db.get_or_404(Review, review_id)
        user = current_user()
        if user.role != "admin" and review.user_id != user.id:
            abort(403)
        if review.photo_filename:
            try:
                (UPLOAD_DIR / review.photo_filename).unlink(missing_ok=True)
            except OSError:
                pass
        db.session.delete(review)
        db.session.commit()
        flash("Review deleted.", "success")
        return redirect(url_for("admin_dashboard" if user.role == "admin" else "dashboard"))

    @app.route("/admin")
    @admin_required
    def admin_dashboard():
        reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
        reviews = Review.query.order_by(Review.created_at.desc()).all()
        users = User.query.order_by(User.id.asc()).all()
        return render_template("admin_dashboard.html", reservations=reservations, reviews=reviews, users=users)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/robots.txt")
    def robots():
        sitemap_url = url_for("sitemap", _external=True)
        return f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n", 200, {"Content-Type": "text/plain"}

    @app.route("/sitemap.xml")
    def sitemap():
        home_url = url_for("home", _external=True)
        xml = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
               "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
               f"<url><loc>{home_url}</loc></url></urlset>")
        return xml, 200, {"Content-Type": "application/xml; charset=utf-8"}

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("error.html", code=403, message="You do not have permission to view this page."), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="We couldn't find that page."), 404

    @app.errorhandler(413)
    def file_too_large(_error):
        flash("That upload is too large. The maximum file size is 5 MB.", "danger")
        return redirect(url_for("dashboard"))

    with app.app_context():
        db.create_all()
        if os.getenv("SEED_DEMO", "1") == "1":
            if not User.query.filter_by(email="admin@pawfect.test").first():
                db.session.add(User(name="Pawfect Admin", email="admin@pawfect.test", password_hash=generate_password_hash("PawfectAdmin123!"), role="admin"))
            if not User.query.filter_by(email="customer@pawfect.test").first():
                db.session.add(User(name="Demo Customer", email="customer@pawfect.test", password_hash=generate_password_hash("Pawfect123!"), role="customer"))
            db.session.commit()
    return app


app = create_app()

if __name__ == "__main__":
    # Local development only. For public hosting use gunicorn (configured in Render setup).
    app.run(debug=True)
