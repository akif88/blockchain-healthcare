from flask import Flask, render_template, request, redirect, url_for, flash, session, g

import localdb
import blockchain

app = Flask(__name__)

@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/login')
@app.route('/login/<name>', methods=('GET', 'POST'))
def login(name=None):
    db = localdb.get_db()  # get local DB connection

    # Provider Page
    if name == 'provider':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            error = None

            # check valid username
            user = db.execute('select id from provider where providername=? and password=?',
                              (username, password)).fetchone()

            if user is None:
                error = 'user is not valid'

            if error is not None:
                flash(error)
            else:
                return redirect(url_for('provider', uid=user, uname=username))

        return render_template('login.html', name=name)

    # Patient Page
    elif name == 'patient':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            error = None

            if not username:
                error = 'Error!!!'

            if error is not None:
                flash(error)
            else:
                return redirect(url_for('patient', uname=username))

        return render_template('login.html', name=name)

    # Miner Page
    elif name == 'miner':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            error = None

            # check valid username
            user = db.execute('select * from miner where minername=? and password=?',
                              (username, password)).fetchone()

            if user is None:
                error = 'user is not valid'

            if error is not None:
                flash(error)
            else:
                return redirect(url_for('miner', uname=username))

        return render_template('login.html', name=name)

    elif name is None:
        return redirect(url_for('index_page'))

    return render_template('login.html')


@app.route('/provider', methods=('GET', 'POST'))
@app.route('/provider/<name>', methods=('GET', 'POST'))
def provider(name=None):
    db = localdb.get_db()
    provider_id = request.args['uid']
    name = request.args['uname']

    # page posted
    if request.method == 'POST':
        id_patient = 1
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Error!!!'

        if error is not None:
            flash(error)
        else:
            db.execute('INSERT INTO patient VALUES (?,?,?,?)',
                       (id_patient, username, password, "AS"))
            db.commit()
            blockchain.create_patient_account(username, password, "provider")
            return redirect(url_for('provider', uid=provider_id, uname=name))

    # get patient username in DB while provider page first load
    # just now!!!, provider view them with permission!!!!!!!
    patientname = db.execute('select username from patient').fetchall()
    if name is not None:
        return render_template('provider.html', name=name, patientname=patientname)

    return render_template('provider.html')


@app.route('/patient')
@app.route('/patient/<name>', methods=('GET', 'POST'))
def patient(name=None):
    name = request.args['uname']
    if name is not None:
        return render_template('patient.html', name=name)

    return render_template('patient.html')


@app.route('/miner', methods=('GET', 'POST'))
@app.route('/miner/<name>', methods=('GET', 'POST'))
def miner(name=None):
    name = request.args['uname']

    if request.method == 'POST':
        blockchain.mining(user="miner")
        return redirect(url_for("miner", uname=name))

    if name is not None:
        return render_template('miner.html', name=name)

    return render_template('miner.html')


@app.route('/logout')
def logout():
    #session.clear()
    return redirect(url_for('index_page'))


if __name__ == '__main__':
    app.run()
