#encoding: utf-8
__author__ = 'ST'

from flask import Flask, render_template, request, session, redirect, url_for
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kami'
Bootstrap(app)


@app.route('/', methods=['POST', 'GET'])
def home_page():
    con = True  # TODO set connection state here
    password = '123456'  # TODO set pass word here
    card_init = True  # TODO set card init state here
    card_left = 100   # TODO set card left money here
    card_uid = 11     # TODO set card uid here

    if request.method == 'POST':
        if request.form['action'] == 'login':
            err = ''
            if not con:
                err = u'请插卡'
                return render_template('home_page.html', err=err, msg=None)

            post_password = request.form['pass']

            if post_password != password:
                err = u'密码错误'
                return render_template('home_page.html', err=err, msg=None)

            session['card_uid'] = card_uid
            return redirect('/')

        if request.form['action'] == 'logout':
            session['card_uid'] = -1
            return redirect('/')

        if request.form['action'] == 'init':
            # TODO init card here
            msg = 'succeed'
            return msg

        if request.form['action'] == 'add':
            # TODO add some money here
            msg = 'succeed'
            return msg

        if request.form['action'] == 'sub':
            # TODO sub some money here
            msg = 'succeed'
            return msg

        return u'未知的请求：' + request.form['action']

    if card_uid == session.get('card_uid'):
        card = {'init': card_init, 'left': card_left, 'uid': card_uid}
        return render_template('my_home.html', card=card)

    err = ''
    if not con:
        err = u'请插卡'
    return render_template('home_page.html', err=err, msg=None)


if __name__ == '__main__':
    app.run(debug=True)
