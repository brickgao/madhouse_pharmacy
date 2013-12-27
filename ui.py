#encoding: utf-8
__author__ = 'ST'

from flask import Flask, render_template, request, session, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from mwic import make_conn, check_password, publish_card
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kami'
Bootstrap(app)


@app.route('/', methods=['POST', 'GET'])
def home_page():
    con, dev = make_conn()

    card_init = True  # TODO set card init state here
    card_left = 100   # TODO set card left money here
    card_uid = 11     # TODO set card uid here
    con = True
    if request.method == 'POST':
        if request.form['action'] == 'login':
            err = ''
            if not con:
                err = u'请插卡'
                return render_template('home_page.html', err=err, msg=None)

            post_password = request.form['pass']

            if not not check_password(dev, post_password):
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
            if not publish_card(dev):
                msg = u'发卡失败'
            return msg

        if request.form['action'] == 'add':
            # TODO add some money here
            count = request.form['count']
            c = 0
            msg = 'succeed'
            try:
                c = float(count)
            except Exception, e:
                if count == '':
                    msg = u'请输入数字'
                else:
                    msg = u'数字中不能出现其他字符'
            else:
                index = count.rfind('.')
                if (index > -1 and index + 3 < len(count)) or index == len(count) - 1:
                    msg = u'数字精度有误或者小数点后没有数字'
                elif c <= 0:
                    msg = u'数字必须大于0'
                elif card_left + c > 100000:
                    msg = u'卡中金额过多或者充值金额过大，请先购药'
                elif '+' in count:
                    msg = u'数字中不能出现其他字符'
            return msg

        if request.form['action'] == 'sub':
            # TODO sub some money here
            count = request.form['count']
            c = 0
            msg = 'succeed'
            try:
                c = float(count)
            except Exception, e:
                if count == '':
                    msg = u'请输入数字'
                else:
                    msg = u'数字中不能出现其他字符'
            else:
                index = count.rfind('.')
                if (index > -1 and index + 3 < len(count)) or index == len(count) - 1:
                    msg = u'数字精度有误或者小数点后没有数字'
                elif c <= 0:
                    msg = u'数字必须大于0'
                elif card_left - c < 0:
                    msg = u'余额不足，请先充值'
                elif '+' in count:
                    msg = u'数字中不能出现其他字符'
            return msg

        return u'未知的请求：' + request.form['action']

    if card_uid == session.get('card_uid'):
        card = {'init': card_init, 'left': card_left, 'uid': card_uid}
        return render_template('my_home.html', card=card)

    err = ''
    if not con:
        err = u'请插卡'
    return render_template('home_page.html', err=err, msg=None)

def run():
    app.run(debug=False)

if __name__ == '__main__':
    app.run(debug=True)
