from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import uuid

# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid.uuid1())


# Create a Form Class
# https://wtforms.readthedocs.io/en/3.0.x/fields/
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


## Custom Error Page(s)
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

