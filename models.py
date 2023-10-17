from unicodedata import category
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager
from enum import unique


db=SQLAlchemy()
login=LoginManager()
class UserModel(UserMixin,db.Model):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(100),unique=True)
    username=db.Column(db.String(100))
    password_hash=db.Column(db.String(250))


    def set_password(self,password):
        self.password_hash= generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    


class CategoryMaster(db.Model):
    category_id=db.Column(db.Integer, primary_key=True)
    category_name=db.Column(db.String(100),nullable=False)

    blogmodel=db.relationship('BlogModel',backref='categorymaster', lazy=True)



class BlogModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id=db.Column(db.Integer,db.ForeignKey('category_master.category_id'),nullable=False)
    blog_user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    blog_text=db.Column(db.Text,nullable=False)
    blog_creation_date=db.Column(db.DateTime)
    blog_read_count=db.Column(db.Integer,default=0)
    blog_rating_count=db.Column(db.Integer,default=0)
    comments = db.relationship('BlogComment', backref='blog', lazy=True)

    author = db.relationship('UserModel', backref='blogs', foreign_keys=blog_user_id)

  
    
class BlogComment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    blog_id=db.Column(db.Integer,db.ForeignKey('blog_model.id'),nullable=True)
    blog_comment=db.Column(db.Text)
    comment_user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=True)
    blog_rating=db.Column(db.Integer)
    blog_comment_date=db.Column(db.DateTime)

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
