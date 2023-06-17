from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    rut = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)

    muestras = db.relationship('Muestra', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "rut": self.rut,
            "email": self.email,
            "rol": self.rol
        }

class Muestra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(150), nullable=False)
    ubication = db.Column(db.String(120), nullable=False)
    ubication_image = db.Column(db.String(120), nullable=False)
    area = db.Column(db.String(80), nullable=False)
    specimen = db.Column(db.String(80), nullable=False)
    quality_specimen = db.Column(db.String(80), nullable=False)
    image_specimen = db.Column(db.String(80), nullable=False)
    aditional_comments = db.Column(db.String(80), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='muestras')

    def serialize(self):
        return {
            "id": self.id,
            "project_name": self.project_name,
            "ubication": self.ubication,
            "ubication_image": self.ubication_image,
            "area": self.area,
            "specimen": self.specimen,
            "quality_specimen": self.quality_specimen,
            "image_specimen": self.image_specimen,
            "aditional_comments": self.aditional_comments
        }
