from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "1234567"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(120))

    def __init__(self, blog_title, blog_body):
        self.blog_title = blog_title
        self.blog_body = blog_body


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    id = request.query_string
    if request.method == 'GET':
        if not id:
            return render_template('blog.html', blogs = blogs)
        else:
            b = str(request.args.get('b'))
            blog = Blog.query.get(b)
            return render_template('singlepost.html', blog = blog)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
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
            new_post = Blog(blog_title, blog_body)
            db.session.add(new_post)
            db.session.commit()

            b = new_post.id
            blog = Blog.query.get(b)
            return render_template('singlepost.html', blog = blog)

        return redirect('/blog')

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()