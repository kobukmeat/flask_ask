from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.models import Question, Answer, User, Board
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')


@bp.route('/list/')
def _list():
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    question_list = Question.query.order_by(Question.create_date.desc())
    board_id = request.args.get('board_id', type=int)
    if board_id:
        question_list = question_list.filter(Question.board_id == board_id)
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문 제목
                    Question.content.ilike(search) |  # 질문 내용
                    User.username.ilike(search) |  # 질문 작성자
                    sub_query.c.content.ilike(search) |  # 답변 내용
                    sub_query.c.username.ilike(search)  # 답변 작성자
                    ) \
            .distinct()
    question_list = question_list.paginate(page=page, per_page=10)
    boards = Board.query.all()

    return render_template('question/question_list.html', question_list=question_list, boards=boards, selected_board_id=board_id, page=page, kw=kw)


@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    # 조회수 초기화 및 증가
    if question.view_count is None:  # None일 경우 0으로 초기화
        question.view_count = 0
    question.view_count += 1
    db.session.commit()
    board_id = request.args.get('board_id', type=int)
    boards = Board.query.all()
    return render_template('question/question_detail.html',boards=boards,selected_board_id=board_id, question=question, form=form)


@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = QuestionForm()
    form.board_id.choices = [(board.id, board.name) for board in Board.query.all()]
    board_id = request.args.get('board_id', type=int)
    boards = Board.query.all()

    # 특정 키워드 리스트
    restricted_keywords = ['시발', '섹스', 'ㅅㅅ', '시12발']  # 여기에 금지어 추가


    if request.method == 'POST' and form.validate_on_submit():
        if any(keyword in form.subject.data for keyword in restricted_keywords) or any(keyword in form.content.data for keyword in restricted_keywords):
            flash('제목이나 내용에 금지된 단어가 포함되어 있습니다. 정신차리세요', 'danger')
            return render_template('question/question_form.html', boards=boards, selected_board_id=board_id, form=form)

        question = Question(subject=form.subject.data, content=form.content.data,
                            create_date=datetime.now(), user=g.user,
                            board_id=form.board_id.data)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', boards=boards,selected_board_id=board_id, form=form)


@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    boards = Board.query.all()  # 모든 게시판 목록

    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    form = QuestionForm(obj=question)  # 기존 질문 데이터를 사용하여 폼 초기화
    form.board_id.choices = [(board.id, board.name) for board in boards]  # 게시판 선택지 설정

    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(question)  # 폼 데이터를 질문 객체에 반영
            question.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))

    # GET 요청 시, 기본 선택 값으로 질문의 게시판을 설정
    form.board_id.data = question.board_id  # 수정할 질문의 게시판 ID를 기본 선택으로 설정

    return render_template('question/question_form.html', boards=boards, form=form)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))


@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user == question.user:
        flash('본인이 작성한 글은 추천할수 없습니다')
    else:
        question.voter.append(g.user)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))