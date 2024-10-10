from backend import db
from datetime import datetime
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # BORROWED or RETURNED
    date = db.Column(db.DateTime, default=datetime.utcnow,nullable=False)

    def __repr__(self):
        return f'History {self.id}'