from app import app, db
from app.forms import LoginForm, RegistrationForm, NewRegistrationForm
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user
from app.models import User, InCom
from flask_login import login_required, logout_user
from werkzeug.urls import url_parse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import timezone


@app.route('/')
@app.route('/all_registrations')
@login_required
def all_registrations():
    all_registrations_query = InCom.query.order_by(InCom.id.desc()).all()
    for registration in all_registrations_query:
        registration.order_link = f'https://zamowienia.konsport.com.pl/pl/zamowienia/pdf/' \
                                  f'{registration.order_number}/zamowienie/false'
        registration.local_timestamp = registration.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime(
            '%d/%m/%Y')
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
        registration.timestamp = registration.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime(
            '%d/%m/%Y')
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


@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = username
    return render_template('profile.html', title='Profil', user=user)


@app.route('/change_status/<reg_id>', methods=['GET', 'POST'])
@login_required
def change_status(reg_id):
    to_change = InCom.query.filter_by(id=reg_id).first()
    to_change.registration_status = 'ZAKOŃCZONE'
    db.session.commit()
    flash(f'Zmieniono status Zgłoszenia ID={reg_id}')
    return redirect(url_for('user_registrations', username=current_user.username))


@app.route('/get_report/<id_to_report>')
def get_report(id_to_report):
    report_query = InCom.query.filter_by(id=id_to_report).first()
    data_report = {
        'ID ZGŁOSZENIA': id_to_report,
        'NUMER ZLECENIA': report_query.order_number,
        'DATA ZGŁOSZENIA':
            report_query.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%d/%m/%Y %H:%M:%S'),
        'ZGŁASZAJĄCY': report_query.user_id,
        'OBSZAR WYKRYCIA': report_query.detection_area,
        'RODZAJ': report_query.product_type,
        'MODEL': report_query.model,
        'PRZYCZYNA': report_query.cause,
        'OPIS': report_query.description,

    }
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    report = canvas.Canvas(f"reports/RW_{id_to_report}.pdf")
    report.setFont('Arial', 12)
    report.drawString(150, 800, f'REKLAMACJA WEWNĘTRZNA')
    for i, key in enumerate(data_report):
        report.drawString(50, 780 - (i * 20), f'{key}: {data_report[key]}')
    report.save()
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '/reports/'
    return send_from_directory(filepath, f'RW_{id_to_report}.pdf')
