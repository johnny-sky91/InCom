from app import app, db
from app.forms import LoginForm, RegistrationForm, NewRegistrationForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user
from app.models import User, InCom
from flask_login import login_required, logout_user
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/all_registrations')
@login_required
def all_registrations():
    all_registrations_query = InCom.query.order_by(InCom.id.desc()).all()
    for registration in all_registrations_query:
        registration.order_link = f'https://zamowienia.konsport.com.pl/pl/zamowienia/pdf/' \
                                  f'{registration.order_number}/zamowienie/false'
        registration.user_name = User.query.filter_by(id=registration.user_id).first().username
    return render_template("all_registrations.html", title='Wszystkie RW', all_registrations=all_registrations_query)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('all_registrations'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nieprawidłowa nazwa użytkownika lub hasło')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('all_registrations')
        return redirect(next_page)
    return render_template('login.html', title='Zaloguj się', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('all_registrations'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('all_registrations'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Zarejestrowaleś się!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Zarejestruj się', form=form)


@app.route('/user_registrations/<username>')
@login_required
def user_registrations(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_registrations_query = InCom.query.filter_by(user_id=current_user.id).order_by(InCom.id.desc()).all()
    for registration in user_registrations_query:
        registration.order_link = f'https://zamowienia.konsport.com.pl/pl/zamowienia/pdf/' \
                                  f'{registration.order_number}/zamowienie/false'
    return render_template('user_registrations.html', user=user, title='Zgłoszone RW',
                           user_registrations=user_registrations_query)


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
        return redirect(url_for('user_registrations', username=current_user.username))

    return render_template('new_registration.html', title='Nowe RW', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # TODO wypełnić radosną tfurczosciom
    return render_template('profile.html', title='Profil')


# TODO funkcja do zmiany statusu zlecenia
@app.route('/change_status/<reg_id>', methods=['GET', 'POST'])
@login_required
def change_status(reg_id):
    to_change = InCom.query.filter_by(id=reg_id).first()
    to_change.registration_status = 'ZAKOŃCZONE'
    db.session.commit()
    flash(f'Zmieniono status Zgłoszenia ID={reg_id}')
    return redirect(url_for('user_registrations', username=current_user.username))
