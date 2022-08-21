from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from sqlalchemy import exc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LogInForm, CommentForm
from flask_gravatar import Gravatar

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
# create an instance of the LoginManager class
login_manager = LoginManager()
# initialize and configure you application with flask login
login_manager.init_app(app)


# Configure Gravatar to your application
gravatar = Gravatar(app=app, size=100, rating='g', default='retro', force_default=False,force_lower=False,use_ssl=False,base_url=None)


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final_blog_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLES
base = declarative_base()


class User(UserMixin, db.Model, base):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    # the property children creates a relationship with its child table blogpost
    # children = relationship('BlogPost',back_populates = 'parent')
    # posts = relationship('BlogPost', back_populates='user_author')
    # read the comments below for extra information

    posts = relationship('BlogPost', back_populates='author')
    # creating a one to many bidirectional relationship with the comments table
    # where a user can have multiple comments, but a comment can only belong to a particular user

    comment_usr = relationship('Comment', back_populates='user_comment')


class BlogPost(db.Model, base):
    __tablename__ = "blog_posts"
    # what the above line does is create a table in the database with the above given name
    # this is useful in case you do not want a table with the same name as the class that you just created
    id = db.Column(db.Integer, primary_key=True)

    # comment the author column to avoid redundancy
    # author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # author_is column is the extra column  in the table blogpost which will be the foreign key in
    # reference to the user.id, what it does is to link the two table together where the user.id and author
    # id are similar, the column is created just like any other, just that it takes an extra argument ForeignKey()
    # which takes the name of the specific column that will be the foreignkey as a string
    # do not forget that a column can only be a foreignkey if its unique in its parent table
    # author_id = db.Column(db.Integer,ForeignKey('user.id'), nullable=False)
    # the parent property is used to link back to the parent table which in this case is the user table
    # the above format is to create a bidirectional relationship where you can query the table
    # from either the parent or the child
    # parent = relationship('User',back_populates = 'children')

    # creating a property to join the two database you will create it using the relationship() which takes several
    # arguments which are the name of the table or in this case the class of the table, and which also takes
    # the specific keyword argument back_populates='' as the property name from the inverse table you want to join
    # user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    # user_author = relationship('User', back_populates='post')
    # our current database has some form of redundancy where as you will see we have two columns in the two table
    # with similar data the name, author in user and blogpost respectively, what you could do is since the two tables
    # already have a relationship is you can access data from either end, assume you want to access the name
    # from the blogpost object  is you could tap in to the property which holds the relationship and it
    # would point you to the other table and you can access the name as you have been the previous number of times

    author_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    author = relationship('User', back_populates='posts')
    # create a bidirectional relationship with the child table comment
    comment = relationship('Comment', back_populates='blog')


class Comment(db.Model, UserMixin, base):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    comment_text = db.Column(db.String, nullable=False)
    # a single blog can have many comments, therefore a one to many relationship
    # create a column in the comment table that will store the blog ids as the foreign keys
    # in this instance the blog is the parent and the comment is the child

    # create a relationship with the parent table BlogPost

    blog_id = db.Column(db.Integer, ForeignKey('blog_posts.id'), nullable=False)
    blog = relationship('BlogPost', back_populates='comment')

    # create a relationship with the parent table User
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    user_comment = relationship('User', back_populates='comment_usr')


db.create_all()


# create a decorator function to handle users from manually typing the routes eg make-post, delete, update-post
# and accessing the admin privileges
# a decorator function is a function that wraps another function inside

def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        print(current_user.id)
        if current_user.id != 1:
            return abort(403)
        return function(*args, **kwargs)

    return wrapper_function


# create a Flasklogin method to facilitate object reloading and functionality of the library
# know as the userloader which is an attribute of the object loadmanager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def get_all_posts():
    posts = BlogPost().query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=['POST', "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.data['name']
        password = form.data['password']
        email = form.data['email']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        print(name, email, hashed_password)
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            login_user(user)
            flash("You are now logged in!")
            return redirect(url_for('get_all_posts'))
        except exc.IntegrityError:
            flash("The account already exist, try to login!")
            return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        email = form.data['email']
        password = form.data['password']
        user = User.query.filter_by(email=email).first()
        # the check_password_hash() takes two parameters which is the hashed password and the password if they match
        # the function will return true and false otherwise
        if user:
            if check_password_hash(user.password, password=password):
                print("matched")
                flash("You were successfully logged in")
                login_user(user)
                print(current_user.id)
                for blogs in current_user.posts:
                    print(blogs.title)

                return redirect(url_for('get_all_posts'))
            else:
                flash("The password is incorrect, Please try again!")
        else:
            flash("Invalid Email")
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    print(requested_post.author.name)

    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            print(form.data['text'])
            if form.data['text'] !='':
                comm = Comment(comment_text = form.data['text'], blog_id=post_id, user_id=current_user.id)
                db.session.add(comm)
                db.session.commit()
                return redirect(url_for('show_post',post_id=post_id))
            else:
                return redirect(url_for('show_post',post_id=post_id))

        else:
            flash(message="Please login in or register to save your comment")
            return redirect(url_for('login'))


    return render_template("post.html", post=requested_post, form=form, comments=requested_post.comment)
    # whats going to happen when the post route is visited the requested_post holds all the available posts inside and
    # their records
    # the database which are joined together using a relationship so incase you want to get the individual comments
    # for the blog post you will use the attribute provided in the table of the blog called comment which holds the
    # reference point, this will return all the comments of the specif blog as a list which you will loop through
    # and display the subsequent comments, when displaying the author of the comments name, what will happen
    # is now since we are currently in the comment table we will utilise the attribute that joins the comment table
    # and the user table which in this case is user_comment, this will be as follows requested_post.comment.user_comment
    # will return a list of the individual author comment objects, an to print the author name since we are now
    # pointing at the user table we can tapin to the name attribute


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["POST", "GET"])
@login_required
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        print(current_user)
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["POST", "GET"])
@login_required
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        # post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@login_required
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='127.0.1.0', port=5000, debug=True)
