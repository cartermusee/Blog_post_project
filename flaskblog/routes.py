from flask import render_template,url_for, redirect, flash,abort, request,session
from flaskblog import app,db,bcrypt
from flaskblog.modules import User,Post
from flaskblog.files import Registration,Login, AccountUpdateForm,PostForm,RequestResetForm,ResetPassword
from flask_login import login_user,current_user,logout_user,login_required
from flaskblog import mail
from flask_mail import Message


@app.route("/")
@app.route("/home")
# @login_required
def home():
    """function for home page"""
    page = request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template("home.html",posts=posts)

@app.route("/about/")
def about():
    """function for about page"""
    return render_template("about.html",title="About")

@app.route("/register", methods=['GET', 'POST'])
def register():
    """method for register a user"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Registration()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data,password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your Account {} was created for {} you can now login!".format(form.email.data, form.username.data), 'success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route("/login", methods=['GET',"POST"])
def login():
    """function for user to login and authenticate user"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for("home"))
        else:
            flash("unsuccessful login check your email and username",'danger')
    return render_template('login.html',title='Login',form=form)

@app.route("/logout")
def logout():
    """logout function"""
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET',"POST"])
@login_required
def account():
    """function for the account page"""
    form = AccountUpdateForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("yor account has been updated",'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='images/{}'.format(current_user.image_file))
    return render_template('account.html', image_file=image_file,form=form)

@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    """function for creating a new post"""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("post is posted",'success')
        return redirect(url_for('home'))
    return render_template('create_post.html',form=form, legend= 'New Post')


@app.route("/post/<int:post_id>",methods=['GET','POST'])
@login_required
def post(post_id):
    """function for a single post"""
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',post=post)



@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
    """function to update a post"""
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title= form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post has been updated succefully', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='update post', form=form, legend= 'update Post')

@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    """functon to delete a post"""
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted succefully', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
@login_required
def user_posts(username):
    """function to check a single user post and display them"""
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=2)
    return render_template("user_post.html",posts=posts,user=user)

def send_reset_email(user):
    """functionto verify the reset token"""
    token = user.get_reset_token()
    msg = Message('passwword Reset Request',
                  sender='cartermusee@gmail.com',
                  recipients=[user.email])
    msg.body = f''' to reset password visit the following link:
    {url_for('reset_token',token=token,_external=True)}
    if you did not request this ignore'''
    mail.send(msg)


@app.route("/reset_password",methods=['GET','POST'])
def reset_request():
    """Reset request page"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been send with instructions to reset password","info")
        return redirect(url_for('login'))
    return render_template('reset_request.html',form=form)

@app.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    """"reset token page function"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token","warning")
        return redirect(url_for('reset_request'))
    form = ResetPassword()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated you can now login!",'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',form=form)

