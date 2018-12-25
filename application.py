#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import session as login_session
from flask import flash
from flask import abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Model, Carmaker
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
import requests as http_requests

app = Flask(__name__)
app.secret_key = 'Super secret key'
engine = create_engine('sqlite:///models.db', echo=True)
Session = sessionmaker(bind=engine)

# OAuth variables
GOOGLE_CLIENT_ID = "1078045580907-7a91vsj3851lecbfm5o9dpb74r5vhtsf\
.apps.googleusercontent.com"
GITHUB_CLIENT_ID = "babe76f240ec18424005"
GITHUB_CLIENT_SECRET = "dbc594d500e154b107071242d8b1769e421498b7"


def serializeModel(self):
    """Serializes model information

    Returs a model as a serialized dict making it easier to present a series
    of models in a list. This is mostly useful when returing JSON.

    Returns:
        A dict of the key elements of a model.
    """
    return {
        'id': self.id,
        'name': self.name,
        'information': self.information
    }


def login_required(secure_page):
    """Checks if a user is logged in an routes them appropriately
    This method protects the data,
    only users who are logged in can modify the data.
    """
    @wraps(secure_page)
    def wrapper(*args, **kwargs):
        userid = login_session.get('userid')
        if userid:
            return secure_page(*args, **kwargs)
        else:
            flash("Please login to view this page.")
            source = request.path
            app.logger.debug(source)
            return redirect(url_for('Login', source_url=source))
    return wrapper


@app.route('/hello')
def HelloWorld():
    return "Hello World"


@app.route('/')
@app.route('/carmakers')
def Home():
    session = Session()
    carmakers = session.query(Carmaker).order_by(Carmaker.name).all()
    return render_template('carmakers.html',
                           carmakers=carmakers)


@app.route('/carmaker/<id>')
@app.route('/models')
def CategoricalModelList(id=None):
    session = Session()
    current_user = login_session.get('userid')
    if id:
        models = session.query(Model).filter(Model.carmaker_id == id).all()
        carmaker = session.query(Carmaker).filter(Carmaker.id == id).one()
        carmaker_name = carmaker.name
        carmaker_author = carmaker.author
        if current_user == carmaker_author:
            owner = True
        else:
            owner = False
    else:
        models = session.query(Model).all()
        carmaker_name = None
        owner = False
    return render_template('models.html',
                           models=models,
                           id=id,
                           carmaker_name=carmaker_name,
                           owner=owner)


# this method to return json
@app.route('/carmaker/<id>/JSON')
def CategoricalModelListJSON(id):
    session = Session()
    models = session.query(Model).filter(Model.carmaker_id == id).all()
    return jsonify(models=[serializeModel(model) for model in models])


@app.route('/carmaker/new', methods=['GET', 'POST'])
@login_required
def NewCarmaker():
    session = Session()
    if request.method == 'POST':
        newCarmaker = Carmaker(name=request.form['name'],
                               author=login_session.get('userid'))
        session.add(newCarmaker)
        session.commit()
        return redirect(url_for('Home'))
    else:
        return render_template('newcarmaker.html')


@app.route('/carmaker/update_<id>', methods=['GET', 'POST'])
@login_required
def UpdateCarmaker(id):
    session = Session()
    carmakerToUpdate = session.query(Carmaker).filter(
        Carmaker.id == id).one()
    current_user = login_session.get('userid')
    if request.method == 'POST':
        if current_user == carmakerToUpdate.author:
            carmakerToUpdate.name = request.form['name']
            session.add(carmakerToUpdate)
            session.commit()
            return redirect(url_for('Home'))
        else:
            return abort(403)
    else:
        if current_user == carmakerToUpdate.author:
            return render_template('updatecarmaker.html',
                                   name=carmakerToUpdate.name,
                                   id=id)
        else:
            return abort(403)


@app.route('/carmaker/delete_<id>', methods=['GET', 'POST'])
@login_required
def DeleteCarmaker(id):
    session = Session()
    carmakerToDelete = session.query(Carmaker).filter(
        Carmaker.id == id).one()
    current_user = login_session.get('userid')
    if request.method == 'POST':
        if current_user == carmakerToDelete.author:
            session.delete(carmakerToDelete)
            session.commit()
            return redirect(url_for('Home'))
        else:
            return abort(403)
    else:
        if current_user == carmakerToDelete.author:
            return render_template('deletecarmaker.html',
                                   name=carmakerToDelete.name,
                                   id=id)
        else:
            return abort(403)


@app.route('/models/JSON')
def ModelListJSON():
    model_list = {}
    session = Session()
    carmakers = session.query(Carmaker).all()
    for carmaker in carmakers:
        models = (
            session.query(Model).filter(Model.carmaker_id == carmaker.id).all()
        )
        model_list[carmaker.id] = {
            'name': carmaker.name,
            'models':
            (
                [serializeModel(model)for model in models]
            )
        }
    return jsonify(model_list)


@app.route('/model/<id>')
def ShowModel(id):
    session = Session()
    model = session.query(Model).filter(Model.id == id).one()
    current_user = login_session.get('userid')
    if current_user == model.author:
        owner = True
    else:
        owner = False
    return render_template('model.html',
                           model=model,
                           owner=owner)


@app.route('/model/<id>/JSON')
def ShowModelJSON(id):
    session = Session()
    model = session.query(Model).filter(Model.id == id).one()
    return jsonify(id=model.id, name=model.name,
                   information=model.information
                   )


@app.route('/model/new', methods=['GET', 'POST'])
@login_required
def NewModel():
    session = Session()
    author = login_session.get('userid')
    if request.method == 'POST':
        newModel = Model(
            name=request.form['name'],
            information=request.form['information'],
            carmaker_id=request.form['carmaker'],
            author=author,
        )
        session.add(newModel)
        session.commit()
        return redirect(url_for('ShowModel', id=newModel.id))
    else:
        app.logger.debug(
            'User logged in as {}'.format(login_session['userid'])
        )
        carmakers = session.query(Carmaker).all()
        return render_template('newmodel.html', carmakers=carmakers)


@app.route('/model/update_<id>', methods=['GET', 'POST'])
@login_required
def UpdateModel(id):
    session = Session()
    modelToUpdate = session.query(Model).filter(
        Model.id == id).one()
    current_user = login_session.get('userid')
    if request.method == 'POST':
        if current_user == modelToUpdate.author:
            modelToUpdate.name = request.form['name']
            modelToUpdate.information = request.form['information']
            modelToUpdate.carmaker_id = request.form['carmaker']
            session.add(modelToUpdate)
            session.commit()
            return redirect(url_for('ShowModel', id=id))
        else:
            return abort(403)
    else:
        carmakers = session.query(Carmaker).all()
        if current_user == modelToUpdate.author:
            return render_template('updatemodel.html',
                                   name=modelToUpdate.name,
                                   information=modelToUpdate.information,
                                   id=id,
                                   carmaker=modelToUpdate.carmaker.name,
                                   carmakers=carmakers)
        else:
            return abort(403)


@app.route('/model/delete_<id>', methods=['GET', 'POST'])
@login_required
def DeleteModel(id):
    session = Session()
    modelToDelete = session.query(Model).filter(
        Model.id == id).one()
    current_user = login_session.get('userid')
    if request.method == 'POST':
        if current_user == modelToDelete.author:
            session.delete(modelToDelete)
            session.commit()
            return redirect(url_for('Home'))
        else:
            return abort(403)
    else:
        if current_user == modelToDelete.author:
            return render_template('deletemodel.html',
                                   name=modelToDelete.name,
                                   id=id)
        else:
            return abort(403)


@app.route('/login')
def Login():
    user_id = login_session.get('userid')
    app.logger.debug(user_id)
    if user_id:
        return render_template('login.html',
                               logged_in=True,
                               provider=login_session.get('provider'),
                               user=login_session.get('username'))
    else:
        source_url = request.args.get('source_url')
        app.logger.debug(source_url)
        return render_template('login.html',
                               logged_in=False,
                               source_url=source_url,
                               github_client_id=GITHUB_CLIENT_ID)


@app.route('/logout', methods=['POST'])
def Logout():
    if login_session.get('userid'):
        provider = login_session.get('provider')
        user = login_session.get('username')
        user_id = login_session.get('userid')
        app.logger.debug(login_session)
        login_session.pop('userid')
        flash("User {} @ {} logged out.".format(user, provider))
        return redirect(url_for('Login'))
    else:
        flash("No user was logged in, so logout is unnecessary.")
        return redirect(url_for('Login'))


@app.route('/googleoauth', methods=['POST'])
def GoogleOAuth():
    try:
        idinfo = (id_token.verify_oauth2_token(request.form['idtoken'],
                                               requests.Request(),
                                               GOOGLE_CLIENT_ID))

        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            return 'Wrong issuer.'

        login_session['provider'] = 'Google'
        login_session['userid'] = idinfo['sub']
        login_session['username'] = idinfo['name']
        flash("You have successfully logged in via Google as {}"
              .format(idinfo['email']))
        return "{} id {}".format(idinfo['email'], login_session['userid'])
    except ValueError:
        # Invalid token
        return "Invalid Token"


@app.route('/githuboauth', methods=['GET', 'POST'])
def GithubOAuth():
    if request.args.get('code'):
        user_oauth_code = request.args.get('code')

        """Generate a request to the GitHub auth portal using the code
        provided via the redirect_uri from GitHub's authentication flow. The
        POST request will return a JSON object containing the information
        from the User's profile.
        """
        request_url = 'https://github.com/login/oauth/access_token'
        bearer_token = {'client_id': GITHUB_CLIENT_ID,
                        'client_secret': GITHUB_CLIENT_SECRET,
                        'code': user_oauth_code
                        }
        header = {'Accept': 'application/json'}
        get_access_token = http_requests.post(request_url,
                                              bearer_token,
                                              headers=header)
        access_token = get_access_token.json()['access_token']
        userurl = ('https://api.github.com/user?access_token={}'
                   .format(access_token))
        get_user_data = http_requests.get(userurl)
        user_json = get_user_data.json()

        # Specify Github-specific token info
        login_session['provider'] = 'Github'
        login_session['userid'] = user_json['id']
        login_session['username'] = user_json['name']
        flash("You have successfully logged in via Github as {}"
              .format(user_json['name']))
        return redirect(url_for('Login'))
    else:
        flash("No authorization was provided. Try again.")
        return redirect(url_for('Login'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
