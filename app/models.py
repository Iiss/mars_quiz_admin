from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db
from . import login_manager
from flask import current_app
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Permission:
    MANAGE_QUIZ = 0x01
    PUBLISH = 0x02
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64),unique = True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref = 'role')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (None, True),
            'Moderator': (Permission.MANAGE_QUIZ |
                          Permission.PUBLISH, False),
            'Administrator': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True, index = True)
    name = db.Column(db.String(64), unique = True, index = True)
    surname = db.Column(db.String(64), unique = True, index = True)
    phone_number = db.Column(db.String(64))
    organization = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default = False)
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions = 0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    
    #temp macros
    @staticmethod
    def clear_table():
        user_list = User.query.all()
        for u in user_list:
            User.query.filter_by(id=u.id).delete()
        db.session.commit()
        print 'User table cleared'

    @staticmethod
    def parse_invite_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        user_id = data.get('confirm')
        if user_id is None:
            return None

        user = User.query.filter_by(id = user_id).first()
        return user

    def generate_reset_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email = new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def delete(self):
        db.session.delete(self)

    def __repr__(self):
        return '<User %r>' % self.name

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

''' Quiz content data classes '''
executives = db.Table('executives',
    db.Column('quiz_id', db.Integer, db.ForeignKey('quizzes.id'), nullable = False),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable = False)
)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(128))
    publish_allowed = db.Column(db.Boolean, default = False)
    tasks = db.relationship('Task', backref = 'quiz')
    executives = db.relationship('User',
                                  secondary = executives,
                                  backref = db.backref('quiz_list', lazy = 'dynamic'),
                                  lazy = 'dynamic')

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(128))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    answers = db.relationship('Answer', backref = 'task')

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key = True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    is_correct = db.Column(db.Boolean, default = False)


