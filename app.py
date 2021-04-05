
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

equipe_members = db.Table('equipe_members',
                          db.Column('iduser', db.Integer, db.ForeignKey('user.id')),
                          db.Column('id_equipe', db.String(15), db.ForeignKey('equipe.id_equipe')),
                          db.Column('leader', db.Boolean, nullable=False, default=True)
                          )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(20), nullable=False)
    prenom = db.Column(db.String(25), nullable=False)
    cin = db.Column(db.String(8), nullable=False)
    date_nai = db.Column(db.DateTime, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    num_tel = db.Column(db.String(15), nullable=False)
    email_user = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False)
    date_de_contrat = db.Column(db.DateTime, nullable=False)
    date_fi_contrat = db.Column(db.DateTime, nullable=False)
    poste = db.Column(db.String(30), nullable=False)
    id_type_contrat = db.Column(db.String(10), db.ForeignKey('type_contrat.id_type_contrat'), nullable=False)
    appearance = db.relationship('Equipe', secondary=equipe_members, backref=db.backref('members', lazy='dynamic'))
    conges = db.relationship('Conge', backref='owner')

    def __init__(self, id, id_type_contrat, nom, prenom, cin, date_nai, username, password, num_tel,
                 email_user, role, date_de_contrat, date_fi_contrat, poste):
        self.id = id
        self.id_type_contrat = id_type_contrat
        self.nom = nom
        self.prenom = prenom
        self.cin = cin
        self.date_nai = date_nai
        self.username = username
        self.password = password
        self.num_tel = num_tel
        self.email_user = email_user
        self.role = role
        self.date_de_contrat = date_de_contrat
        self.date_fi_contrat = date_fi_contrat
        self.poste = poste


class UserSchema(ma.Schema):
    class Meta:
        fields = ['id', 'id_type_contrat', 'nom', 'prenom', 'cin', 'date_nai',
                  'username', 'password', 'num_tel', 'email_user', 'role',
                  'date_de_contrat', 'date_fi_contrat', 'poste']


class Equipe(db.Model):
    id_equipe = db.Column(db.String(15), primary_key=True)

    def __init__(self, id_equipe):
        self.id_equipe = id_equipe


class Type_contrat(db.Model):
    id_type_contrat = db.Column(db.String(10), primary_key=True)
    users = db.relationship('User', backref='owner')

    def __init__(self, id_type_contrat):
        self.id_type_contrat = id_type_contrat


class Type_contratSchema(ma.Schema):
    class Meta:
        fields = ['id_type_contrat']


class Conge(db.Model):
    id_type_conge = db.Column(db.String(30), db.ForeignKey('type_conge.id_type_conge'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    date_de_conge = db.Column(db.DateTime, nullable=False)
    date_fi_conge = db.Column(db.DateTime, nullable=False)

    def __init__(self, id_type_conge, id_user, date_de_conge, date_fi_conge):
        self.id_type_conge = id_type_conge
        self.id_user = id_user
        self.date_de_conge = date_de_conge
        self.date_fi_conge = date_fi_conge


class Type_conge(db.Model):
    id_type_conge = db.Column(db.String(30), primary_key=True)

    def __init__(self, id_type_conge):
        self.id_type_conge = id_type_conge


class Email(db.Model):
    id_email = db.Column(db.String(100), db.ForeignKey('user.email_user'), nullable=False)
    date = db.Column(db.DateTime)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    object_em = db.Column(db.String(50), unique=True, nullable=False)
    contenu = db.Column(db.Text, unique=True, nullable=False)
    destination = db.Column(db.String(100), nullable=False)

    def __init__(self, id_email, date, id_user, object_em, contenu, destination):
        self.id_email = id_email
        self.date = date
        self.id_user = id_user
        self.object_em = object_em
        self.contenu = contenu
        self.destination = destination


class Template_email(db.Model):
    key = db.Column(db.String(20), primary_key=True)
    object_tem = db.Column(db.String(50))
    contenu = db.Column(db.Text)

    def __init__(self, key, object_tem, contenu):
        self.key = key
        self.object_tem = object_tem
        self.contenu = contenu


class Jour_feriee(db.Model):
    nom_jour_feriee = db.Column(db.String(25), primary_key=True)
    date_d_jf = db.Column(db.DateTime, nullable=False)
    date_f_jf = db.Column(db.DateTime, nullable=False)

    def __init__(self, nom_jour_feriee, date_d_jf, date_f_jf):
        self.nom_jour_feriee = nom_jour_feriee
        self.date_d_jf = date_d_jf
        self.date_f_jf = date_f_jf


class Jour_ferieeSchema(ma.Schema):
    class Meta:
        fields = ['nom_jour_feriee', 'date_d_jf', 'date_f_jf']


@app.route('/jourFeriee', methods=['GET'])
def getuser():
    alljours = Jour_feriee.query.all()
    jourf = Jour_ferieeSchema(many=True)
    result = jourf.dump(alljours)
    return jsonify(result)


@app.route('/jourFeriee/add', methods=['POST'])
def add_date():
    data_data = request.get_json()
    jour_f = Jour_feriee(nom_jour_feriee=data_data['nom_jour_feriee'],
                         date_d_jf=data_data['date_d_jf'], date_f_jf=data_data['date_f_jf'])
    db.session.add(jour_f)
    db.session.commit()
    return jsonify(data_data)


@app.route('/users', methods=['GET'])
def get_users():
    allusers = User.query.all()
    users = UserSchema(many=True)
    res = users.dump(allusers)
    return jsonify(res)


@app.route('/users/add', methods=['POST'])
def add_user():
    data_user = request.get_json()
    users = User(id=data_user['id'], id_type_contrat=data_user['id_type_contrat'], nom=data_user['nom'],
                 prenom=data_user['prenom'], cin=data_user['cin'], username=data_user['username'],
                 password=data_user['password'], date_nai=data_user['date_nai'],
                 num_tel=data_user['num_tel'], email_user=data_user['email_user'],
                 role=data_user['role'], date_de_contrat=data_user['date_de_contrat'],
                 date_fi_contrat=data_user['date_fi_contrat'], poste=data_user['poste'])
    db.session.add(users)
    db.session.commit()
    return jsonify(data_user)


@app.route('/accounts', methods=['GET'])
def get_accounts():
    all_accounts = User.query.with_entities(User.id, User.username, User.password)
    acc_users = UserSchema(many=True)
    acc_res = acc_users.dump(all_accounts)
    return jsonify(acc_res)


@app.route('/typcontrat/add', methods=['POST'])
def add_contrat():
    data_contrat = request.get_json()
    contrats = Type_contrat(id_type_contrat=data_contrat['id_type_contrat'])
    db.session.add(contrats)
    db.session.commit()


@app.route('/typcontrat', methods=['GET'])
def get_contrats():
    allcontrats = Type_contrat.query.all()
    contrats = Type_contratSchema(many=True)
    res_cont = contrats.dump(allcontrats)
    return jsonify(res_cont)


if __name__ == '__main__':
    app.run()
