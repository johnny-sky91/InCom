from app import app, db
from app.forms import LoginForm, RegistrationForm, NewComplaintForm, NewAreaForm
from app.models import User, InCom, DetectionAreas, Types, Models, Causes
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user
from flask_login import login_required, logout_user
from werkzeug.urls import url_parse
import os
from datetime import timezone, datetime
import flask_excel as excel
from collections import Counter, defaultdict


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


@app.route('/')
@app.route('/all_complaints')
@login_required
def all_complaints():
    return render_template('all_complaints.html', title='All complaints')


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
        if col_name not in ['id', 'user_id', 'detection_area', 'timestamp', 'product_type',
                            'model', 'cause', 'description', 'complaint_status']:
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
        if os.environ.get('LINK') is None:
            order_number_link = x["order_number"]
        else:
            order_number_link = os.environ.get('LINK').replace('to_replace', x["order_number"])
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


@app.route('/user_complaints/<username>')
@login_required
def user_complaints(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_complaints_query = InCom.query.filter_by(user_id=current_user.id).order_by(InCom.id.desc()).all()
    for complaint in user_complaints_query:
        if os.environ.get('LINK') is None:
            complaint.order_link = complaint.order_number
        else:
            complaint.order_link = os.environ.get('LINK').replace('to_replace', complaint.order_number)
        complaint.timestamp = complaint.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime(
            '%d/%m/%Y')
    return render_template('user_complaints.html', user=user, title=f'User complaints - {username}',
                           user_complaints=user_complaints_query)


@app.route('/change_status/<reg_id>', methods=['GET', 'POST'])
@login_required
def change_status(reg_id):
    to_change = InCom.query.filter_by(id=reg_id).first()
    to_change.complaint_status = 'CLOSED'
    db.session.commit()
    flash(f'Complaint ID={reg_id} status changed')
    return redirect(url_for('user_complaints', username=current_user.username))


@app.route('/get_report/<id_to_report>', methods=['GET'])
def get_report(id_to_report):
    report_query = InCom.query.filter_by(id=id_to_report).all()
    for row in report_query:
        row.user_id = User.query.filter_by(id=row.user_id).first().username
    return render_template('report.html', title=f'Report ID:{id_to_report}', report_data=report_query)


@app.route('/new_complaint', methods=['GET', 'POST'])
@login_required
def new_complaint():
    form = NewComplaintForm()

    areas_query = DetectionAreas.query.with_entities(DetectionAreas.detection_area).filter_by(user_id=current_user.id)
    areas = [item for t in areas_query for item in t]
    form.detection_area.choices = areas

    types_query = Types.query.with_entities(Types.product_type)
    types = [item for t in types_query for item in t]
    form.product_type.choices = types

    models_query = Models.query.with_entities(Models.product_model)
    models = [item for t in models_query for item in t]
    form.model.choices = models

    causes_query = Causes.query.with_entities(Causes.cause_type)
    causes = [item for t in causes_query for item in t]
    form.cause.choices = causes

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


@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    return render_template('profile.html', title=f'Profile - {username}')


@app.route('/add_new_area/<username>', methods=['GET', 'POST'])
@login_required
def add_new_area(username):
    form = NewAreaForm()
    if form.validate_on_submit():
        new_area = DetectionAreas(
            user_id=current_user.id,
            detection_area=f'{form.new_area.data}'
        )
        db.session.add(new_area)
        db.session.commit()
        flash('A new area was added to the department')
        return redirect(url_for('profile', username=username))
    return render_template('new_area.html', title='Add new area', form=form)


@app.route('/download_csv', methods=['GET'])
def download_csv():
    excel.init_excel(app)
    result = defaultdict(list)
    for row in InCom.query.all():
        res = row.__dict__
        res.pop('_sa_instance_state')
        for key in res:
            result[key].append(res[key])
    return excel.make_response_from_dict(result, file_type='csv', file_name='InCom data.csv')


@app.route('/basic_chart', methods=['GET'])
def basic_chart():
    year = datetime.today().isocalendar()[0]
    week = datetime.today().isocalendar()[1]
    all_week = {}
    for x in range(1, 6):
        day = datetime.strptime(f"{year}-W{week}-{x}", "%Y-W%W-%w").strftime("%d-%m-%Y")
        all_week[day] = 0

    dates_query = InCom.query.with_entities(InCom.timestamp)
    dates = [item.strftime("%d-%m-%Y") for t in dates_query for item in t]

    dates_dict = dict(Counter(dates))

    to_chart = {**all_week, **dates_dict}
    labels = []
    values = []
    for key in to_chart:
        if key in all_week.keys():
            labels.append(key)
            values.append(to_chart[key])
    legend = ['Number of internal complaints']
    return render_template('basic_chart.html', title='Basic chart', labels=labels, values=values, legend=legend)
