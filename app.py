from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor

import uuid as uuid
import os

# Create a Flask Instance
app = Flask(__name__)

# Add CKEditor
ckeditor = CKEditor(app)

# SQLite3 Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.app_context().push()

# MySQL Database (mysql://<username>:<password>@<serverip>/<db_name>)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://db-admin:password@localhost/our_users'
app.app_context().push()

# Create a CSRF Secret Key
# app.config['SECRET_KEY'] = str(uuid.uuid1())
app.config['SECRET_KEY'] = 'MySuperSecretKey'

# Setup Folder for Uploading Images
UPLOAD_FOLDER = './static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize & Migrate Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

## Routes ##
# Root Route
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

# Login Page Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user:
            # Check Password Hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login Successful')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong Password')
        else:
            flash('Invalid Username')
    return render_template('login.html', form = form)

# Dashboard Page Route
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']
        
        # Grab Image Name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        # Save Profile Pic
        saver = request.files['profile_pic']
        
        # Override profile_pic to be just a String in Database
        name_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
            flash("User Updated Successfully")
            return render_template('dashboard.html',
                form = form,
                name_to_update = name_to_update)
        except:
            flash("Database Error!")
            return render_template('dashboard.html',
                form = form,
                name_to_update = name_to_update)
    else:
        return render_template('dashboard.html',
                form = form,
                name_to_update = name_to_update,
                id = id)


# Admin Route
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 16:
        return render_template('admin.html')
    else:
        flash('You must be an administrator to access this page')
        return redirect(url_for('dashboard'))

# Logout Page Route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Succesfully Logged Out')
    return redirect(url_for('login'))


# Blog Home Page
@app.route('/posts')
def posts():
    # Grab all posts from database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts = posts)


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
            user = Users(name = form.name.data,
                username = form.username.data,
                email = form.email.data, 
                fav_color = form.fav_color.data,
                password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
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
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        name_to_update.username = request.form['username']
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
@login_required
def delete(id):
    if id == current_user.id:
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
    else:
        flash("You do not have permission to delete that user!")
        return redirect(url_for('dashboard'))


# JSON Page
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}


# Post Page
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, 
            content=form.content.data,
            poster_id=poster,
            slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''

        # Add Post data to Database
        db.session.add(post)
        db.session.commit()
        flash("Blog Post submitted successfully!")

    # Redirect to webpage
    return render_template('add_post.html', form=form)


# View Individual Post Page
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


# Edit Post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        #Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post was updated successfully")
        return redirect(url_for('post', id=post.id))
    if current_user.id == post.poster_id:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You are not authorized to edit that post")
        return redirect(url_for('posts', posts=posts))


# Pass params/args to base.html then to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# Search Route
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', 
            form=form,
            searched=post.searched,
            posts=posts)


# Delete Post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    # id = current_user.id
    if current_user.id == post_to_delete.poster_id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post deleted successfully!')
            # Grab all posts from database and display
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts = posts)
        except:
            flash('There was an issue deleting that post')
            # Grab all posts from database and display
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts = posts)
    else:
        flash('You are not authorized to delete that post')
        # Grab all posts from database and display
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts = posts)


## Custom Error Page(s) ##
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


## Database Models ##
# Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign Key to link Users (primary key: user,id)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# User Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    fav_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    # User can have many posts - need database relationship
    posts = db.relationship('Posts', backref='poster')
    profile_pic = db.Column(db.String(120), nullable=True)

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
