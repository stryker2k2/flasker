from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
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

# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

## Form Classes
# https://wtforms.readthedocs.io/en/3.0.x/fields/
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    fav_color = StringField("Favorite Color")
    submit = SubmitField("Submit")

class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
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
            user = Users(name=form.name.data, 
                email=form.email.data, 
                fav_color = form.fav_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.fav_color.data = ''
        flash('User Added Successfully!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html',
        form = form, 
        name = name,
        our_users = our_users)

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



## Custom Error Page(s)
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

