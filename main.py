from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.exceptions import BadRequestKeyError
import random
import string


LIST_ID_LENGTH = 6
current_date = datetime.now().strftime("%d %B %Y")


def generate_random_string():
    result = ''.join(random.choice(string.ascii_letters) for i in range(LIST_ID_LENGTH))
    if ListData.query.filter_by(list_id=result).first():
        generate_random_string()
    return result


app = Flask(__name__)
app.config['SECRET_KEY'] = 'uyze7r5tu6i987ozer54u7iuyu4y5u5y6'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lists_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)
db = SQLAlchemy(app)
app.app_context().push()


class ListData(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    creation_date = db.Column(db.String(80), nullable=False)
    list_id = db.Column(db.String(80), nullable=False)
    list_name = db.Column(db.String(80), nullable=False)


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    data = ListData.query.all()
    generate_id = generate_random_string()
    if request.method == 'POST':
        new_entry = ListData(
            text=request.form.get('text'),
            status='open',
            creation_date=current_date,
            list_id=generate_id,
            list_name='List name'
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('create_list', list_id=generate_id))
    return render_template('index.html', data=data, generate=generate_id)


@app.route('/create/<list_id>', methods=['GET', 'POST'])
def create_list(list_id):
    data = ListData.query.filter_by(list_id=list_id).all()
    try:
        # this is to rename the list:
        if request.args['TitleText'] != '':
            text = request.args['TitleText']
            for item in data:
                item.list_name = text
            db.session.commit()
            return redirect(url_for('create_list', list_id=list_id))
        # =============================
    except BadRequestKeyError:
        if request.method == 'POST':
            new_entry = ListData(
                text=request.form.get('text'),
                status='open',
                creation_date=current_date,
                list_id=list_id,
                list_name='List name'
            )
            db.session.add(new_entry)
            db.session.commit()
            return redirect(url_for('create_list', list_id=list_id))
    return render_template('create.html', list_id=list_id, data=data)


@app.route('/delete/<list_id>/<id>')
def delete(id, list_id):
    item = ListData.query.filter_by(id=id).first()
    list_id = item.list_id
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('create_list', list_id=list_id))


@app.route('/update/<list_id>/<id>')
def update(id, list_id):
    item = ListData.query.filter_by(id=id).first()
    listid = item.list_id
    if item.status == 'completed':
        item.status = 'open'
        db.session.commit()
        return redirect(url_for('create_list', list_id=listid))
    else:
        item.status = 'completed'
        db.session.commit()
        return redirect(url_for('create_list', list_id=listid))


@app.route('/settings/<id>', methods=['GET', 'POST'])
def settings(id):
    title_text = request.args.get('TitleText=')
    data = ListData.query.filter_by(list_id=id).all()
    for item in data:
        item.list_name = title_text
        db.session.commit()
    return redirect(request.url)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
