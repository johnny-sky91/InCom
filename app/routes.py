from app import app, db
from app.forms import LoginForm, RegistrationForm, NewComplaintForm, NewAreaForm
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user
from app.models import User, InCom, DetectionAreas
from flask_login import login_required, logout_user
from werkzeug.urls import url_parse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import timezone, datetime
from collections import Counter

@app.route('/')
@app.route('/all_complaints')
def all_complaints():
    return render_template('all_complaints.html', title='All complaints')


@app.route('/user_complaints/<username>')
@login_required
def user_complaints(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_complaints_query = InCom.query.filter_by(user_id=current_user.id).order_by(InCom.id.desc()).all()
    for complaint in user_complaints_query:
        complaint.order_link = f'https://zamowienia.konsport.com.pl/pl/zamowienia/pdf/' \
                               f'{complaint.order_number}/zamowienie/false'
        complaint.timestamp = complaint.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime(
            '%d/%m/%Y')
    return render_template('user_complaints.html', user=user, title=f'User complaints - {username}',
                           user_complaints=user_complaints_query)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('all_complaints'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('all_complaints')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('all_complaints'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('all_complaints'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have signed up')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign up', form=form)


@app.route('/new_complaint', methods=['GET', 'POST'])
@login_required
def new_complaint():
    form = NewComplaintForm()

    areas_query = DetectionAreas.query.with_entities(DetectionAreas.detection_area).filter_by(user_id=current_user.id)
    areas = [item for t in areas_query for item in t]
    form.detection_area.choices = areas

    if form.validate_on_submit():
        incom = InCom(
            user_id=current_user.id,
            order_number=form.order_number.data,
            product_type=form.product_type.data,
            model=form.model.data,
            cause=form.cause.data,
            detection_area=form.detection_area.data,
            description=form.description.data
        )
        db.session.add(incom)
        db.session.commit()
        flash('New complaint added')
        return redirect(url_for('user_complaints', username=current_user.username))

    return render_template('new_complaint.html', title=f'New complaint - {current_user.username}', form=form)


@app.route('/change_status/<reg_id>', methods=['GET', 'POST'])
@login_required
def change_status(reg_id):
    to_change = InCom.query.filter_by(id=reg_id).first()
    to_change.complaint_status = 'CLOSED'
    db.session.commit()
    flash(f'Complaint ID={reg_id} status changed')
    return redirect(url_for('user_complaints', username=current_user.username))


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
    report = canvas.Canvas('reports/RW.pdf')
    report.setFont('Arial', 12)
    report.drawString(150, 800, f'REKLAMACJA WEWNĘTRZNA')
    for i, key in enumerate(data_report):
        report.drawString(50, 780 - (i * 20), f'{key}: {data_report[key]}')
    report.save()
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '/reports/'
    return send_from_directory(filepath, f'RW.pdf')


@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    return render_template('profile.html', title=f'Profile - {username}')


@app.route('/add_new_area', methods=['GET', 'POST'])
@login_required
def add_new_area():
    form = NewAreaForm()
    if form.validate_on_submit():
        new_area = DetectionAreas(
            user_id=current_user.id,
            detection_area=f'{form.new_area.data}'
        )
        db.session.add(new_area)
        db.session.commit()
        flash('A new area was added to the department')
        return redirect(url_for('profile', username=current_user.username))
    return render_template('new_area.html', title='Add new area', form=form)


@app.route('/basic_chart', methods=['GET'])
def basic_chart():
    year = datetime.today().isocalendar()[0]
    week = datetime.today().isocalendar()[1]
    all_week = {}
    for x in range(1, 6):
        day = datetime.strptime(f"{year}-W{week}-{x}", "%Y-W%W-%w").strftime("%Y-%m-%d")
        all_week[day] = 0
    dates_query = InCom.query.with_entities(InCom.timestamp)
    dates = [item.strftime("%Y-%m-%d") for t in dates_query for item in t]
    for x in dates:
        if x not in all_week.keys():
            dates.remove(x)
    data = dict(Counter(dates))
    to_chart = {**all_week, **data}
    labels = list(to_chart.keys())
    values = list(to_chart.values())
    return render_template('basic_chart.html', title='Basic chart', labels=labels, values=values)


@app.route('/api/data')
def data():
    query = InCom.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            InCom.description.like(f'%{search}%'),
            InCom.order_number.like(f'%{search}%')
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['id', 'user_id', 'order_number']:
            col_name = 'id'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(InCom, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    final_data = [user.to_dict() for user in query]
    for x in final_data:
        order_number_link = f'https://zamowienia.konsport.com.pl/pl/zamowienia/pdf/{x["order_number"]}/zamowienie/false'
        order_number_link = f"<a href={order_number_link}>{x['order_number']}</a>"
        local_timestamp = x["timestamp"].replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%d/%m/%Y')
        user = User.query.filter_by(id=x["user_id"]).first().username
        x.update({'order_number': order_number_link, 'timestamp': local_timestamp, 'user_id': user})
    # response
    return {
        'data': final_data,
        'recordsFiltered': total_filtered,
        'recordsTotal': InCom.query.count(),
    }
