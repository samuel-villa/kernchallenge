from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kern_timesheet_app.auth import login_required
from kern_timesheet_app.db import get_db

import datetime

bp = Blueprint('timesheet', __name__)


@bp.route('/')
def index():
    db = get_db()
    timesheets = db.execute(
        'SELECT t.id, checkin, checkout, user_id'
        ' FROM timesheet t JOIN user u ON t.user_id = u.id'
        ' ORDER BY checkin DESC'
    ).fetchall()
    return render_template('timesheet/index.html', timesheets=timesheets)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':

        # TODO checkout logic
        timecheck = datetime.datetime.now()
        # checkin = timecheck.strftime("%a %d %b %Y %H:%M:%S")
        checkin = timecheck
        # checkout = None
        error = None

        if not checkin:
            error = 'Checkin is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO timesheet (checkin, user_id)'
                ' VALUES (?, ?)',
                (checkin, g.user['id'])
            )
            db.commit()
            return redirect(url_for('timesheet.index'))

    return render_template('timesheet/create.html')


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
            return redirect(url_for('timesheet.index'))

    return render_template('timesheet/update.html', timesheet=timesheet)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_timesheet(id)
    db = get_db()
    db.execute('DELETE FROM timesheet WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('timesheet.index'))
