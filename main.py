from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm, CreateHotelForm, DeleteForm
from functools import wraps
import os

app = Flask(__name__)
API_KEY = os.getenv("HOTEL_API_KEY")
app.config['SECRET_KEY'] = os.getenv("gi")
ckeditor = CKEditor(app)
Bootstrap(app)
##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', "sqlite:///hotels.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.__init__(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if not current_user.is_authenticated:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


with app.app_context():
    class User(UserMixin, db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(100))
        new_hotels = relationship("Hotel", back_populates="creator")


    db.create_all()

with app.app_context():
    class Hotel(db.Model):
        __tablename__ = "hotels"
        id = db.Column(db.Integer, primary_key=True)
        creator_id = db.Column(db.Integer, db.ForeignKey("users.id"))
        name = db.Column(db.String(250), unique=True, nullable=False)
        creator = relationship("User", back_populates="new_hotels")
        hotel_location = db.Column(db.String(500), nullable=False)
        img_url = db.Column(db.String(1000), nullable=False)
        hotel_address = db.Column(db.String(500), nullable=False)
        hotel_description = db.Column(db.Text, nullable=False)
        has_wifi = db.Column(db.String(250), nullable=False)
        has_pool = db.Column(db.String(250), nullable=False)
        has_dining = db.Column(db.String(250), nullable=False)
        starting_price = db.Column(db.String(250), nullable=True)
    db.create_all()


@app.route('/')
def home():
    hotels = Hotel.query.all()
    return render_template('index.html', hotels=hotels)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    requested_post = Hotel.query.get(post_id)
    return render_template("hotel.html", post=requested_post, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists, please login")
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8,
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        elif not user:
            flash("Email does not exist")
            return redirect(url_for('login'))
        else:
            flash("Password incorrect")
            return redirect(url_for('login'))
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add-hotel', methods=['GET', 'POST'])
@admin_only
def add_hotel():
    form = CreateHotelForm()
    if form.validate_on_submit():
        new_hotel = Hotel(
            creator=current_user,
            name=form.name.data,
            hotel_location=form.hotel_location.data,
            hotel_address=form.hotel_address.data,
            hotel_description=form.hotel_description.data,
            has_pool=form.has_pool.data,
            img_url=form.img_url.data,
            has_wifi=form.has_wifi.data,
            has_dining=form.has_dining.data,
            starting_price=form.starting_price.data
        )
        db.session.add(new_hotel)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add-hotel.html', form=form, current_user=current_user)


@app.route("/edit-hotel/<int:hotel_id>", methods=['GET', 'POST'])
@admin_only
def edit_hotel(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    edit_form = CreateHotelForm(
        name=hotel.name,
        creator=current_user,
        hotel_location=hotel.hotel_location,
        hotel_address=hotel.hotel_address,
        hotel_description=hotel.hotel_description,
        img_url=hotel.img_url,
        starting_price=hotel.starting_price,
        has_pool=hotel.has_pool,
        has_wifi=hotel.has_wifi,
        has_dining=hotel.has_dining,
    )
    if edit_form.validate_on_submit():
        hotel.name = edit_form.name.data
        hotel.creator = current_user
        hotel.hotel_location = edit_form.hotel_location.data
        hotel.hotel_address = edit_form.hotel_address.data
        hotel.hotel_description = edit_form.hotel_description.data
        hotel.img_url = edit_form.img_url.data
        hotel.starting_price = edit_form.starting_price.data
        hotel.has_pool = edit_form.has_pool.data
        hotel.has_wifi = edit_form.has_wifi.data
        hotel.has_dining = edit_form.has_dining.data
        db.session.commit()
        return redirect(url_for("home", hotel_id=hotel.id))

    return render_template("add-hotel.html", form=edit_form, current_user=current_user, is_edit=True)


@app.route('/delete/<int:hotel_id>', methods=["GET", "POST"])
@admin_only
def delete_hotel(hotel_id):
    form = DeleteForm()
    hotel_to_delete = Hotel.query.get(hotel_id)
    if form.validate_on_submit():
        input_key = form.secret_key.data
        if not input_key == API_KEY:
            flash("The secret key is incorrect")
            return redirect(url_for('delete_hotel', hotel_id=hotel_id))
        else:
            db.session.delete(hotel_to_delete)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('delete.html', form=form, current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True)
