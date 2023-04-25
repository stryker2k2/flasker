from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Create a Flask Instance
app = Flask(__name__)

# SQLite3 Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.app_context().push()

# MySQL Database (mysql://<username>:<password>@<serverip>/<db_name>)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://db-admin:password@localhost/our_users'
app.app_context().push()

# Create a CSRF Secret Key
app.config['SECRET_KEY'] = str(uuid.uuid1())

# Initialize & Migrate Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# User Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Password Stuff
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

# Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))


## Form Classes
# https://wtforms.readthedocs.io/en/3.0.x/fields/
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    fav_color = StringField("Favorite Color")
    submit = SubmitField("Submit")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo("password_hash2", message = "Passwords Must Match!")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])

class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("What's your email?", validators=[DataRequired()])
    password_hash = PasswordField("What's your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Route Decorator
@app.route('/')
def index():
    first_name = 'John'
    bold_stuff = 'This is <strong>BOLD</strong> Text'
    lower_stuff = 'this is bold text'
    fav_pizza = ['Pepperoni', 'Cheese', 'Mushroom', 41]
    return render_template('index.html', 
        user_name = first_name,
        stuff = bold_stuff,
        fav_pizza = fav_pizza)


# localhost:5000/user/john
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', 
        user_name = name)
    

# Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    # https://flask-wtf.readthedocs.io/en/0.15.x/form/
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form Submitted Successfully!')
    return render_template('name.html', 
        name = name, 
        form = form)

# Add User Page
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    # Validate Form
    # https://flask-wtf.readthedocs.io/en/0.15.x/form/
    if form.validate_on_submit():
        name = Users.query.filter_by(email=form.email.data).first()
        if name is None:
            # Hash the Password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, 
                email=form.email.data, 
                fav_color = form.fav_color.data,
                password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.fav_color.data = ''
        form.password_hash.data = ''
        flash('User Added Successfully!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html',
        form = form, 
        name = name,
        our_users = our_users)

# Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    # https://flask-wtf.readthedocs.io/en/0.15.x/form/
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        # Lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()
        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
    return render_template('test_pw.html',
        email = email,
        password = password,
        pw_to_check = pw_to_check,
        passed = passed,
        form = form)

# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template('update.html',
                form = form,
                name_to_update = name_to_update)
        except:
            flash("Database Error!")
            return render_template('update.html',
                form = form,
                name_to_update = name_to_update)
    else:
        return render_template('update.html',
                form = form,
                name_to_update = name_to_update,
                id = id)

# Delete Record from Database
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")

        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html',
            form = form, 
            name = name,
            our_users = our_users)

    except:
        flash("Deleting User Error!")
        return render_template('add_user.html',
            form = form, 
            name = name,
            our_users = our_users)

# JSON Page
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}

# Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, 
            content=form.content.data, 
            author=form.author.data, 
            slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # Add Post data to Database
        db.session.add(post)
        db.session.commit()
        flash("Blog Post submitted successfully!")

    # Redirect to webpage
    return render_template('add_post.html', form=form)



## Custom Error Page(s)
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

