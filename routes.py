from datetime import datetime
from turtle import update
from flask import Flask,render_template,redirect,request,url_for
from flask_login import login_required,current_user,login_user,logout_user
from sqlalchemy import func,text

from models import UserModel,BlogModel,CategoryMaster,BlogComment,db,login


app=Flask(__name__)
app.secret_key='Itshouldbeongnough'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///raj.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)
login.init_app(app)
login.login_view='login'


def get_all_categories():
    global global_all_category_no, global_all_category_name
    all_categories = CategoryMaster.query.all()

    all_category_info = db.session.query(CategoryMaster.category_id, CategoryMaster.category_name).all()

    if not all_category_info:  # Check if the query returned any categories
        global_all_category_no, global_all_category_name = [], []
    else:
        global_all_category_no, global_all_category_name = zip(*all_category_info)


@app.before_request
def create_all():
    with app.app_context():
        db.create_all()
    get_all_categories()
    
@app.route('/')
def route():
    return redirect('/register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/blogs')

    if request.method=='POST':
        email=request.form.get('email')
        user=UserModel.query.filter_by(email=email).first()
        if user is not None and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect('/blogs')
        return render_template('/register.html')
    return render_template('/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/register')


@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/blogs')
    if request.method=='POST':
        email=request.form.get('email')
        username=request.form.get('username')
        password=request.form.get('password')


        if UserModel.query.filter_by(email=email).first():
            return "Email Already Exist"
        
        user=UserModel(email=email,username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/blogs')
    return render_template('register.html')


@app.route('/blogs')
def blogs():
    if current_user.is_authenticated:
        return render_template('blogs_home.html')
    return redirect(url_for('list_all_blogs'))
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import func, text  # Import 'text' from SQLAlchemy
from models import UserModel, BlogModel, CategoryMaster, BlogComment, db, login

# ...
@app.route('/createblog', methods=['GET', 'POST'])
@login_required
def create_blog():
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        blog_text = request.form.get('blog_text')
        today = datetime.now()
        blog_user_id = current_user.id
        blog_read_count = 0
        blog_rating_count = 0

        newBlog = BlogModel(category_id=category_id, blog_user_id=blog_user_id,
                            blog_text=blog_text, blog_creation_date=today,
                            blog_read_count=blog_read_count,
                            blog_rating_count=blog_rating_count)
        db.session.add(newBlog)
        db.session.commit()
        return redirect('/blogs')
    else:
        # Fetch categories directly from the database using SQL query (declare it as text)
        sql_query = text("SELECT category_id, category_name FROM category_master")
        all_categories = db.session.execute(sql_query).fetchall()
        
        # Initialize the global_all_category_name variable
        global_all_category_name = [category[1] for category in all_categories]
        
        # Debugging: Print the categories before rendering the template
        print("All Categories:", global_all_category_name)
        
        return render_template('create_blog.html', all_categories=all_categories)


# ...


@app.route('/viewblog')
@login_required
def view_blogs():
    all_self_blogs=BlogModel.query.filter(BlogModel.blog_user_id==current_user.id).all()
    return render_template('view_blog.html', all_self_blogs=all_self_blogs,all_categories=global_all_category_name)


@app.route('/self_blog_detail/<int:blog_model_id>/<string:blog_model_category>',methods=['GET','POST'])
@login_required
def self_blog_detail(blog_model_id,blog_model_category):
    blog_model=BlogModel.query.get(blog_model_id)

    if request.method=='POST':
        if request.form['action']=='Update':
            blog_model.blog_text=request.form.get('blog_text')
        else:
            BlogModel.query.filter_by(id=blog_model_id).delete()
        db.session.commit()
        return redirect('/viewblog')
    return render_template('self_blog_detail.html',blog_id=blog_model_id,blog_categories=blog_model_category,blog_text=blog_model.blog_text)

@app.route('/ListAllBlogs')
def list_all_blogs():
    all_blogs=BlogModel.query.all()
    all_users=UserModel.query.all()
    all_category_name = [category.category_name for category in CategoryMaster.query.all()]
    print(all_category_name)
    return render_template('list_all_blogs.html',all_blogs=all_blogs,all_users=all_users,all_category_name=all_category_name)


@app.route('/blogdetail/<int:blog_id>/<string:username>/<string:category>', methods=["GET","POST"])
@login_required
def blog_detail(blog_id, username, category):
    blog=BlogModel.query.get(blog_id)
    if request.method=='GET':
        if current_user.id!=blog.blog_user_id:
            blog.blog_read_count=blog.blog_read_count+1
            db.session.commit()
        rating=db.session.query(func.avg(BlogComment.blog_rating)).filter(BlogComment.blog_id==int(blog_id)).first()[0]
        return render_template('blog_detail.html', blog=blog, rating=rating,author=username, category=category)
    else:
        rate=request.form.get('rating')
        comment=request.form.get('comment')
        blog_id=request.form.get('blog_id')
        oldcomment=BlogComment.query.filter(BlogComment.blog_id==blog_id).filter(BlogComment.comment_user_id==current_user.id).first()
        today=datetime.now()

        if oldcomment==None:
            blog.blog_rating_count=blog.blog_rating_count+1

            newcomment=BlogComment(
                blog_id = blog_id,
                comment_user_id= current_user.id,
                blog_comment=comment,
                blog_rating=rate,
                blog_comment_date=today

            )
            db.session.add(newcomment)
        else:
            oldcomment.blog_comment=comment
            oldcomment.blog_rating=rate
        db.session.commit()
        return redirect('/blogs')
if __name__=="__main__":
    app.run(debug=True)
