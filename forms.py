from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class CreateHotelForm(FlaskForm):
    name = StringField('Hotel name', validators=[DataRequired()])
    creator = StringField("Your name", validators=[DataRequired()])
    hotel_location = StringField('Hotel location on google maps (URL)', validators=[DataRequired(), URL()])
    hotel_address = StringField('Hotel address', validators=[DataRequired()])
    hotel_description = CKEditorField('Describe hotel', validators=[DataRequired()])
    img_url = StringField("Hotel Image URL", validators=[DataRequired(), URL()])
    starting_price = StringField("Starting price for rooms in Naira", validators=[DataRequired()])
    has_pool = StringField('Pool available, Yes or No ', validators=[DataRequired()])
    has_wifi = StringField('Wifi available, Yes or No ', validators=[DataRequired()])
    has_dining = StringField('Dining service, Yes or No', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")


class DeleteForm(FlaskForm):
    secret_key = PasswordField("secret_key", validators=[DataRequired()])
    submit = SubmitField("Submit")
