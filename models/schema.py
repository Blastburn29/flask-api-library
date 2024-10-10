from marshmallow import Schema, fields
from .books import Book
from .member import Member
from .history import History
from .librarian import Librarian

class BookSchema(Schema):
    class Meta:
        model = Book
    id = fields.Int()
    title = fields.Str()
    author = fields.Str()
    status = fields.Str()
    borrowed_by = fields.Int()

class MemberSchema(Schema):
    class Meta:
        model = Member
    id = fields.Int()
    username = fields.Str()
    password = fields.Str()
    status = fields.Str()

class HistorySchema(Schema):
    class Meta:
        model = History
    id = fields.Int()
    user_id = fields.Int()
    book_id = fields.Int()
    action = fields.Str()
    date = fields.Date()

class LibrarianSchema(Schema):
    class Meta:
        model = Librarian
    id = fields.Int()
    username = fields.Str()
    password = fields.Str()
