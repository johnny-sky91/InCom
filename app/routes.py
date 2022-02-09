import os
import random
from collections import Counter, defaultdict
from datetime import timezone, datetime

import flask_excel as excel
from flask import render_template, flash, redirect, url_for, request
from flask_babel import _
from flask_login import current_user, login_user
from flask_login import login_required, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, NewComplaintForm, NewAreaForm
from app.models import User, InCom, DetectionAreas, Types, Models, Causes


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
    return render_template('auth/register.html', title=_('Sign up'), form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('all_complaints'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('all_complaints')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Login'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('all_complaints'))


def basic_data(query, column_list):
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
        if col_name not in column_list:
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

    # extra steps
    final_data = [user.to_dict() for user in query]
    for row in final_data:
        # Adding a link to an external website, if any
        if os.environ.get('LINK') is None:
            order_number_link = row["order_number"]
        else:
            order_number_link = os.environ.get('LINK').replace('to_replace', row["order_number"])
            order_number_link = f"<a href={order_number_link}>{row['order_number']}</a>"
        # local timestap from timestap
        local_timestamp = row["timestamp"].replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%d/%m/%Y')
        # username from user_id
        user = User.query.filter_by(id=row["user_id"]).first().username
        row.update({'order_number': order_number_link, 'timestamp': local_timestamp, 'user_id': user})
    # response
    return {
        'data': final_data,
        'recordsFiltered': total_filtered,
        'recordsTotal': InCom.query.count(),
    }


@app.route('/')
@app.route('/complaints_all')
@login_required
def complaints_all():
    return render_template('complaints_all.html', title=_('Complaints - all'))


@app.route('/api/data_complaints_all')
def data_complaints_all():
    query_all = InCom.query
    list_all_complaints_column = ['id', 'user_id', 'detection_area', 'timestamp', 'product_type',
                                  'model', 'cause', 'description', 'complaint_status']
    return basic_data(query_all, list_all_complaints_column)


@app.route('/complaints_user/<username>')
@login_required
def complaints_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    template_title = _('Complaints - user')
    return render_template('complaints_user.html', user=user, title=f'{template_title} - {username}')


@app.route('/api/data_complaints_user')
def data_complaints_user():
    # todo dodanie opcji raportu oraz zmiany statusu zlecenia

    query_all_user = InCom.query.filter_by(user_id=current_user.id)
    list_user_complaints_column = ['id', 'detection_area', 'timestamp', 'product_type',
                                   'model', 'cause', 'description', 'complaint_status']
    result = basic_data(query_all_user, list_user_complaints_column)
    for row in result['data']:
        ic_status = f"<a href={url_for('change_status', reg_id=row['id'])}>{row['complaint_status']}</a>"
        report = f"<a href={url_for('get_report', id_to_report=row['id'])}>{row['id']}</a>"
        row.update({'complaint_status': ic_status, 'id': report})
    return result


@app.route('/change_status/<reg_id>', methods=['GET', 'POST'])
@login_required
def change_status(reg_id):
    to_change = InCom.query.filter_by(id=reg_id).first()
    to_change.complaint_status = _('CLOSED')
    db.session.commit()
    flash(f'Complaint ID={reg_id} status changed')
    return redirect(url_for('user_complaints', username=current_user.username))


@app.route('/get_report/<id_to_report>', methods=['GET'])
def get_report(id_to_report):
    report_query = InCom.query.filter_by(id=id_to_report).first()
    report_query.user_id = User.query.filter_by(id=report_query.user_id).first().username
    template_title = _('Report ID:')
    return render_template('report.html', title=f'{template_title} {id_to_report}', report_data=report_query)


@app.route('/new_complaint', methods=['GET', 'POST'])
@login_required
def complaint_new():
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
    template_title = _('Complaint - new')
    return render_template('complaint_new.html', title=f'{template_title} - {current_user.username}', form=form)


@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    template_title = _('Profile')
    return render_template('profile.html', title=f'{template_title} - {username}')


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
    return render_template('new_area.html', title=_('Add new area'), form=form)


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


@app.route('/ic_quantity_current_week', methods=['GET'])
def ic_quantity_current_week():
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
    legend = [_('Number of internal complaints')]
    axis_x_label = [_('Days of current week')]
    axis_y_label = [_('IC quantity')]
    return render_template('charts/bar_chart.html', title=_('IC quantity - current week'),
                           labels=labels, values=values, legend=legend, axis_x_label=axis_x_label,
                           axis_y_label=axis_y_label)


@app.route('/ic_quantity_all_weeks', methods=['GET'])
def ic_quantity_all_weeks():
    dates_query = InCom.query.with_entities(InCom.timestamp)
    weeks_list = [item[0].isocalendar()[1] for item in dates_query]
    weeks_list = Counter(weeks_list)
    labels = list(weeks_list.keys())
    values = [weeks_list[item] for item in weeks_list]
    legend = [_('Number of internal complaints')]
    axis_x_label = [_('Weeks')]
    axis_y_label = [_('IC quantity')]
    return render_template('charts/bar_chart.html', title=_('IC quantity - all weeks'),
                           labels=labels, values=values, legend=legend,
                           axis_x_label=axis_x_label, axis_y_label=axis_y_label)


@app.route('/ic_quantity_by_cause', methods=['GET'])
def ic_quantity_by_cause():
    causes_query = InCom.query.with_entities(InCom.cause).all()
    causes_list = Counter(causes_query)
    labels = list(causes_list.keys())
    labels = [",".join(item) for item in labels]
    values = [causes_list[item] for item in causes_list]
    legend = [_('Number of internal complaints')]

    def random_hex_color():
        rgb = lambda: random.randint(0, 255)
        return '#%02X%02X%02X' % (rgb(), rgb(), rgb())

    colors = [random_hex_color() for i in range(len(values))]
    return render_template('charts/pie_chart.html', title=_('IC quantity - by cause'),
                           labels=labels, values=values, legend=legend, colors=colors)
