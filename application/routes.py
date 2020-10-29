from flask import render_template, url_for, flash, redirect, request
from application import app, db, bcrypt
from application.forms import RegistrationForm, LoginForm
from application.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json
from os.path import join, dirname, realpath

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


 


def create_plot():
    path_to_file = "application/static/" + current_user.username + "/data.csv"
    loaded_df = pd.read_csv(path_to_file)
    data = [
        go.Scatter(
            x=loaded_df['Time'], # assign x as the dataframe column 'x'
            y=loaded_df['Acc_x']
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='home') 

@app.route("/my_patients")
def my_patients():
    if current_user.is_doctor:
        return render_template('my_patients.html', title='My Patients')
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('home'))

@app.route("/new_patient")
def new_patient():
    if current_user.is_doctor:
        return render_template('new_patient.html', title='New Patient')
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('home'))

@app.route("/graphs", methods=['GET', 'POST'])
@login_required
def graphs():
    if current_user.is_doctor == False:
        bar = create_plot()
        return render_template('graphs.html', plot = bar)
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('home'))

@app.route("/help")
def help():
    return render_template('help.html', title='help') 

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('graphs'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')