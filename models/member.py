from backend import db
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default = "ACTIVE", nullable=False)  # ACTIVE or INACTIVE
    def __repr__(self):
        return f'Member {self.id}'