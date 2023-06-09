# Based on tutorial found on Digital Ocean
import os
from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy


# Set up a database file path
# os.path.abspath() get the absolute path of the current file's dir
# __file__ variable holds the pathname of the current app.py file
BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 

# Instantiate Flask application
app = Flask(__name__)

# Configure 
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(BASE_DIR, 'database.db') # locate database inside project dir
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # escape notifications for every database modificaitons
# app.permanent_session_lifetime = timedelta(days=1)

# connect application with SQLAlchmey
db = SQLAlchemy(app) # or can be connect app using 'db.init_app(app)' after creating SQLAlchemy empty instance


# Declaring Tables 

# Create Post model inherited from db.Model class
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    comments = db.relationship('Comment', backref='post') # create one-to-many reln bn post and comment models

    def __repr__(self):
        return f'<Post "{self.title}">'


# Create Comment Model for comment table inheriting from db.Model class 
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f'<Comment "{self.content[:20]}...">'
    

@app.route('/')
def index():
     posts = Post.query.all()
     return render_template('index.html', posts=posts)

@app.route('/<int:post_id>/', methods=['GET', 'POST'])
def post(post_id):
     # using Model.query() is Legacy query func, according to documentation, prefer use db.session.execute()/ SQLAlchemy.func() instead
     # post = User.query.get_or_404(post_id)
     post = db.get_or_404(Post, post_id)

     if request.method == 'POST':
          comment = Comment(content=request.form['content'], post=post)
          db.session.add(comment)
          db.session.commit()
          return redirect(url_for('post', post_id=post.id))
     
     return render_template('post.html', post=post)


@app.route('/comments/')
def comments():
     comments = db.session.execute(db.select(Comment).order_by(Comment.id.desc())).scalars()
     return render_template('comments.html', comments=comments)
     

@app.post('/comments/<int:comment_id>/delete') # short for app.route('', methods=['POST'])
def delete_comment(comment_id):
     comment = db.get_or_404(Comment, comment_id)
     post_id = comment.post_id
     db.session.delete(comment)
     db.session.commit()
     return redirect(url_for('post', post_id=post_id))


"""Creating Database done by using Flask shell
    with virtual env activated, set the app.py file as your Flask application
    using > $ export FLASK_APP=app
    then  > $ flask shell
    import the database object and the post and comment models, and then run
    db.create_all() function to create the tables associated with your models
    >> from app import db, Post, Comment
    >> db.create_all()

    # post1 = Post(title="Post The First", content='Content for the first post')
    # post2 = Post(title='Post The Second', content='Content for the Second post')
    # post3 = Post(title='Post The Third', content='Content for the third post')

    # # create a few comment objects
    # comment1 = Comment(content='Comment for the first post', post=post1)

    # comment2 = Comment(content='Comment for the second post', post=post2)
    # comment3 = Comment(content='Another comment for the seconde post', post_id=2)
    # comment4 = Comment(content='Another comment for the first post', post_id=1)


    # # add all instance of model or rows of data to the session (making ready for insertion)
    # db.session.add_all([post1, post2, post3])
    # db.session.add_all([comment1, comment2, comment3, comment4])

    # # Then insert into corresponding database tables
# db.session.commit()
"""


if __name__ == '__main__':
	app.run(debug=True)