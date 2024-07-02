from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kern_timesheet_app.auth import login_required
from kern_timesheet_app.db import get_db

bp = Blueprint('timesheet', __name__)


@bp.route('/')
def index():
    db = get_db()
    timesheets = db.execute(
        'SELECT t.id, checkin, checkout, user_id'
        ' FROM timesheet t JOIN user u ON t.user_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('timesheet/index.html', timesheets=timesheets)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        # title = request.form['title']
        checkin = None  # TODO
        checkout = None  # TODO
        error = None
        # --> get current time <--

        if not checkin:
            error = 'Checkin is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO timesheet (checkin, user_id)'
                ' VALUES (?, ?, ?)',
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