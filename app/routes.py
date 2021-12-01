from app import app, db
from app.forms import LoginForm, RegistrationForm, NewRegistrationForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user
from app.models import User, InCom
from flask_login import login_required, logout_user
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
    all_registrations = InCom.query.all()
    return render_template("index.html", title='Wszystkie RW', all_registrations=all_registrations)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Zaloguj się', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Zarejestruj się', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    # TODO ładne błędy dodać xd
    user = User.query.filter_by(username=username).first_or_404()
    zgloszenia = InCom.query.filter_by(user_id=current_user.id)
    return render_template('user.html', user=user, title='Zgłoszone RW', zgloszenia=zgloszenia)


@app.route('/new_registration', methods=['GET', 'POST'])
@login_required
def new_registration():
    form = NewRegistrationForm()
    if form.validate_on_submit():
        incom = InCom(user_id=current_user.id,
                      order_number=form.order_number.data,
                      product_type=form.product_type.data,
                      model=form.model.data,
                      cause=form.cause.data,
                      detection_area=form.detection_area.data,
                      description=form.description.data, )
        db.session.add(incom)
        db.session.commit()
        flash('Przyjęto zgłosznie RW')
        return redirect(url_for('index'))

    return render_template('new_registration.html', title='Nowe RW', form=form)
