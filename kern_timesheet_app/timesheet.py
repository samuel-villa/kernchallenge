from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kern_timesheet_app.auth import login_required
from kern_timesheet_app.db import get_db

import datetime

bp = Blueprint('timesheet', __name__)


INDEX = 'timesheet/index.html'
INDEX_ROUTE = 'timesheet.index'
CREATE = 'timesheet/create.html'


def get_timesheets():
    db = get_db()
    timesheets = db.execute(
        'SELECT t.id, checkin, checkout, user_id'
        ' FROM timesheet t JOIN user u ON t.user_id = u.id'
        ' ORDER BY t.id DESC'
    ).fetchall()
    return timesheets


@bp.route('/')
def index():
    timesheets = get_timesheets()
    return render_template(INDEX, timesheets=timesheets)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'INSERT INTO timesheet (user_id)'
            ' VALUES (?)',
            (g.user['id'],)
        )
        db.commit()
        return redirect(url_for(INDEX_ROUTE))

    return render_template(INDEX)


@bp.route('/<int:id>/checkin', methods=('GET', 'POST'))
@login_required
def checkin(id):
    if request.method == 'POST':
        timecheck = datetime.datetime.now()
        checkin = timecheck
        error = None

        if not checkin:
            error = 'Checkin is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE timesheet SET checkin = ?, user_id = ?'
                ' WHERE id = ?',
                (checkin, g.user['id'], id)
            )
            db.commit()
            timesheets = get_timesheets()
            return render_template(INDEX, timesheets=timesheets)

    return render_template(INDEX)


@bp.route('/<int:id>/checkout', methods=('GET', 'POST'))
@login_required
def checkout(id):
    if request.method == 'POST':

        timecheck = datetime.datetime.now()
        checkout = timecheck
        error = None

        if not checkout:
            error = 'Checkout is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE timesheet SET checkout = ?, user_id = ?'
                ' WHERE id = ?',
                (checkout, g.user['id'], id)
            )
            db.commit()
            timesheets = get_timesheets()
            return render_template(INDEX, timesheets=timesheets)

    return render_template(INDEX)


def get_timesheet(id, check_user=True):
    timesheet = get_db().execute(
        'SELECT t.id, checkin, checkout, user_id'
        ' FROM timesheet t JOIN user u ON t.user_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if timesheet is None:
        abort(404, f"Timesheet id {id} doesn't exist.")

    if check_user and timesheet['user_id'] != g.user['id']:
        abort(403)

    return timesheet


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    timesheet = get_timesheet(id)

    if request.method == 'POST':
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        error = None

        if not checkin:
            error = 'Checkin is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE timesheet SET checkin = ?, checkout = ?'
                ' WHERE id = ?',
                (checkin, checkout, id)
            )
            db.commit()
            return redirect(url_for(INDEX_ROUTE))

    return render_template('timesheet/update.html', timesheet=timesheet)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_timesheet(id)
    db = get_db()
    db.execute('DELETE FROM timesheet WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for(INDEX_ROUTE))
