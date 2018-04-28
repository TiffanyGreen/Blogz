from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "1234567"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_body, owner):
        self.blog_title = blog_title
        self.blog_body = blog_body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique = True)
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by( username = username ).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        email = request.form['email']

        username_error = ''
        password_error = ''
        verify_error = ''
        empty_error= ''
        invalid_email_error=''

        if username.strip()=='' or password.strip()=='' or verify.strip()=='':
            empty_error = 'You forgot to tell us information! Try again.'
        
        if (len(username) < 3) or (len(username) > 19) or username.isalpha() == False:
            username_error = 'Your username is too long or too short. Between 3 and 20 characters is best.'

        if (len(password) < 3) or (len(password) > 19) or password.isalpha() == False:
            password_error = 'Your password is too long or too short. Between 3 and 20 characters is best.'

        if password != verify:
            verify_error= 'Oops! Your passwords must match.'
        
        if email != "" and ((len(email) < 3) or (len(email) > 19) or (email.count ("@") > 1) or (email.count("@") <1) or (email.count (".") > 1) or (email.count(".") <1) or (email.count(" ")>=1)):
            invalid_email_error= 'Please enter a valid email.'
        
        if (not empty_error) and (not username_error) and (not password_error) and (not verify_error) and (not invalid_email_error):
            existing_user = User.query.filter_by(username = username).first()
            if not existing_user:
                new_user = User(username, email, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost?username={0}'.format('username'))
            else:
                # TODO - user better response messaging
                return "<h1> Looks like you've already signed up. Feel free to login.</h1>"

        else:
            return render_template ('signup.html', empty_error = empty_error, username = username, username_error = username_error, password_error = password_error, verify_error = verify_error, invalid_email_error = invalid_email_error)
    else: 
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/index', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html',title="Blog Users!", 
        users = users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()

    if request.method == 'GET':
        ##id = request.args.get('id')
        userId = request.args.get('user') #?user=1
        id = request.args.get('id')
        # if b: render the singlepost
        if request.args.get('id'):
            blogid = Blog.query.get(id)
            bloguser = blogid.owner_id
            userblog = User.query.get(bloguser)
            return render_template('singlepost.html', blog = blogid, user = userblog)
        # else if user: render the users post
        elif request.args.get('user'):
            user = User.query.get(userId)
            return render_template('singleUser.html', user = user )
        # else: render all blogs
        else:
            return render_template('blog.html', blogs = blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    user = User.query.all()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        if not blog_title:
            flash('Please enter a title.')
            return redirect('/newpost')
        if not blog_body:
            flash('Please enter a blog')
            return redirect('/newpost')

        else:
            owner = User.query.filter_by(username = session['username']).first()
            new_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()

            b = new_post.id
            blog = Blog.query.get(b)
            return render_template('singlepost.html', blog = blog)

        return redirect('/blog')

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()