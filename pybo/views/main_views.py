from flask import Blueprint, url_for
from werkzeug.utils import redirect
from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.models import Question, Answer, User, Board
from pybo.views.auth_views import login_required
bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/hello')
def hello_pybo():
    return 'Hello, Pybo!'


@bp.route('/')
def index():
    return redirect(url_for('question._list'))

@bp.route('/usersekdkd')
def usercheck():
    users = User.query.all()
    return render_template('user_ids.html', users=users)