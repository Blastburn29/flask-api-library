from backend import db
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default = "AVAILABLE", nullable=False)  # AVAILABLE or BORROWED
    borrewed_by = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)

    def __repr__(self):
        return f'Book {self.id}'