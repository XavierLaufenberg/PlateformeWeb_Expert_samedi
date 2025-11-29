from flask import Flask, render_template, request, session, redirect, url_for
import pymongo
import os
from dotenv import load_dotenv
import bcrypt
app = Flask(__name__)


#Init
load_dotenv()
# Connect to MongoDB : colle la clé MONGO entre les parenthese de Mongoclient()
# Voir la ressource https://lp-magicmakers.fr/accueil/ressources-makers/menu-flask/base-de-donnees/brancher-sa-bdd/
client = pymongo.MongoClient("mongodb+srv://xavierlaufenberg_db_user:Mot_de_PasseC0nnexi0n@annonces.z1qh6ex.mongodb.net/?appName=Annonces")
db = client["SiteAnnonce"] #ici le nom de la base de donnée

#Clé cookie pour les session utilisateurs
app.secret_key = "70e7XoZu15hl8OQi"

#route pour afficher le template index.html
@app.route('/')
def index():
    annonces_data = list(db["annonces"].find({}))  
    return render_template('index.html', annonces = annonces_data)

#Route pour lancer une recherche
@app.route("/search", methods = ["GET"])
def search():
    query = request.args.get('q', '').strip()

    if query == '':
        results = list(db["annonces"].find({}))
    else: 
        results = list(db["annonces"].find({
            "$or" : [
                {"Titre" : {"$regex" : query, "$options" : "i"} },
                {"Description" : {"$regex" : query, "$options" : "i"} },
                {"Auteur" : {"$regex" : query, "$options" : "i"} }
            ]
        }))

    return render_template("search_result.html", annonces = results, query=query)  

#route login
@app.route("/login", methods = ['POST', 'GET'])
def login():
    #Si on essaye de se connecter on envoie la requete avec le contenu du formulaire
    if request.method == 'POST':
        db_users = db["User"]
        user = db_users.find_one({'User_id' : request.form['user']})
        if user: 
            if request.form['password'] == user['User_password']:
                session['user'] = request.form['user']
                return redirect(url_for('index'))
            else: 
                return render_template('login.html', erreur="mot de passe incorrect")
        else: 
            return render_template('login.html', erreur="Utilisateurs incorrect")
    else: 
        return render_template("login.html")

#route pour se déconnecter
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#route pour s'inscrire au site
@app.route("/register", methods = ['POST' , 'GET'])
def register():
    if request.method == 'POST':
        db_users = db['User']
        if(db_users.find_one({'User_id' : request.form['user']})):
            return render_template('register.html', erreur= "le nom d'utilisateur existe déjà")
        else: 
            if(request.form['password'] ==  request.form['confirm_password']):
                db_users.insert_one({
                    'User_id': request.form['user'],
                    'User_password': request.form['password']
                })
                session['user'] = request.form['user']  
                return redirect(url_for('index'))
            else: 
                return render_template('register.html', erreur= "les mots de passe doivent correspondre")
    else: 
        return render_template('register.html')      

@app.route('/publish', methods = ['POST','GET']) 
def publish():
    if 'user' not in session:
        return render_template('register.html')
    
    if request.method == "POST":
        db_annonces = db['annonces']
        titre = request.form["titre_annonce"]
        description = request.form["descritpion_annonce"]
        auteur = session['user']  

        if titre and description:
            db_annonces.insert_one({
                'Titre' : titre,
                'Description' : description,
                'Auteur' :  auteur
            })
            return redirect(url_for('index'))
        else: 
            return render_template("publish.html", erreur = 'Veuillez remplir tout les champs obligatoires')
    return render_template("publish.html")    
                
#route pour afficher et récupérer les données de la bdd 
@app.route("/test")
def test():
    test_data = list(db["Test"].find({}))  #récupère tous les documents de la collection test
    return render_template('test.html', test=test_data)#affiche le template "test.html" et attribut les bonnes valeurs à la variable test


#Lance l'application
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)