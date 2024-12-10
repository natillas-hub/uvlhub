from app import db


class Deposition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dep_metadata = db.Column(db.JSON, nullable=False)

    def __repr__(self):
        return f'Deposition<{self.id}>'
