from werkzeug.exceptions import HTTPException
# imprtation de flask
from flask import Flask,render_template,request,redirect,url_for
# importation de SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
#from flask.ext.bootstrap import Bootstrap
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

app = Flask(__name__)

# Mise en place de la chaine de connexion à la base de
# données
motdepasse = "Francis"
motdepasse = quote_plus(motdepasse)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:{}@localhost:5432/students".format(
    motdepasse)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# creation d'une instance de la base de données
db = SQLAlchemy(app)
migrate = Migrate(app, db)
Bootstrap(app)

class Etudiant(db.Model):
    __tablename__= 'etudiants'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    adresse = db.Column(db.String(200), nullable=True)
    filiere_id = db.Column(db.Integer, db.ForeignKey('filieres.id', ondelete="CASCADE"), nullable=False)

class Filiere(db.Model):
    __tablename__ = 'filieres'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(50), nullable=False)
    etudiants = db.relationship('Etudiant', backref=db.backref('filieres', lazy=True, cascade="all, delete"))


#Controllers
@app.route("/")
def accueil():
    return render_template('index.html')


@app.route("/filieres")
def liste_filieres():
    filieres = Filiere.query.all()
    return render_template('filieres.html', filieres=filieres)

@app.route("/add_filiere", methods = ['POST', 'GET'])
def creation_filiere():
    if request.method == 'GET':
        return render_template("create.html")
    else:
        libelle = request.form.get('libellefiliere')
        filiere = Filiere(libelle=libelle)
        db.session.add(filiere)
        db.session.commit()
        return redirect(url_for('liste_filieres'))

@app.route("/filieres/<int:id_filiere>", methods = ['GET', "POST", "DELETE"])
def une_filiere(id_filiere):
    filiere = Filiere.query.get(id_filiere)
    if request.method == "GET":
        return render_template('edit-filiere.html', filiere=filiere)
    elif request.method == "POST":
        filiere.libelle = request.form.get("libellefiliere")
        db.session.commit()
        return redirect(url_for("liste_filieres"))

@app.route("/filiere_delete/<int:id>/", methods=['GET', 'POST', 'DELETE'])
def delete_filiere(id):
    filiere = Filiere.query.get(id)
    db.session.delete(filiere)
    db.session.commit()
    return redirect(url_for("liste_filieres"))

@app.route("/etudiants")
def liste_etudiants():
    etudiants = Etudiant.query.join(Filiere, Filiere.id==Etudiant.filiere_id).all()
    return render_template("etudiants.html", etudiants=etudiants)

@app.route("/add_etudiant", methods = ['POST', 'GET'])
def creation_etudiant():
    if request.method == "GET":
        filieres = Filiere.query.all()
        return render_template("etudiant-create.html", filieres=filieres)
    else:
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        adresse = request.form.get("adresse")
        filiere_id = request.form.get("filiere_id")

        etudiant = Etudiant(nom=nom, prenom=prenom, email=email, adresse=adresse, filiere_id=filiere_id)
        db.session.add(etudiant)
        db.session.commit()
        return redirect(url_for("liste_etudiants"))

@app.route("/etudiants/<int:id_etudiant>", methods = ['GET', "POST", "DELETE"])
def un_etudiant(id_etudiant):
    etudiant = Etudiant.query.get(id_etudiant)
    filieres = Filiere.query.all()
    if request.method == "GET":
        return render_template('etudiant-edit.html', etudiant=etudiant, filieres=filieres)
    elif request.method == "POST":
        etudiant.nom = request.form.get("nom")
        etudiant.prenom = request.form.get("prenom")
        etudiant.email = request.form.get("email")
        etudiant.adresse = request.form.get("adresse")
        etudiant.filiere_id = request.form.get("filiere_id")
        db.session.commit()
        return redirect(url_for("liste_etudiants"))

@app.route("/delete/<int:id>/", methods=['GET', 'POST', 'DELETE'])
def delete_etudiant(id):
    etudiant = Etudiant.query.get(id)
    db.session.delete(etudiant)
    db.session.commit()
    return redirect(url_for('liste_etudiants'))


# les errorhandler permettent de capturer les erreurs
@app.errorhandler(404)
def handle_exception(error):
    return render_template("error_pages/404.html",error=error), 404

@app.errorhandler(500)
def handle_exception(error):
    return render_template("error_pages/500.html",error=error), 500


if __name__ == '__main__':
    app.run(DEBUG=True)