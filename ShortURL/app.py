from flask import Flask, g, render_template, session, redirect
import sqlite3

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import random
import string
import datetime

import re, urllib

app = Flask(__name__)

app.config['SECRET_KEY'] = "Andrii_THe_best!"
app.permanent_session_lifetime = datetime.timedelta(hours=1)

DATABASE = 'ShortURL.db'


class LinkForm(FlaskForm):
    name = StringField("Введите длинную ссылку", validators=[DataRequired()])
    submit = SubmitField('ОК')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False, commit=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if commit:
        get_db().commit()
    return (rv[0] if rv else None) if one else rv

def generate_short_link(long_link):
    while True:
        try:
            short_link = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in
                                 range(random.randrange(2, 7)))
            query_db('INSERT INTO links(local_addres,real_addres) VALUES (?, ?)', args=(short_link, long_link),
                     commit=True)
            return short_link
        except:
            pass

@app.route('/', methods=["GET", "POST"])
def que():
    session.permanent = True
    link_input = LinkForm()
    if link_input.validate_on_submit():
        tmp = link_input.name.data
        if tmp.find("http://") != 0 and tmp.find("https://") != 0:
            tmp = "http://" + tmp
        session['long_link'] = tmp
        if re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tmp):
            session['short_link'] = generate_short_link(session.get('long_link'))
            return render_template('index2.html', short_link=session.get('short_link'))
        else:
            return render_template('index3.html')
    return render_template('index.html', form=link_input)

@app.route('/<short_link>')
def short_link_redirect(short_link):
    try:
        tmp = query_db('SELECT real_addres FROM links WHERE local_addres =?', args=(short_link,))[0][0]
        return redirect(tmp)
    except:
        return render_template('index3.html')


if __name__ == '__main__':
    app.run(debug=True)
