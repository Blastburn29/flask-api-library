from flask import jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from backend import db, app
from models.schema import BookSchema, LibrarianSchema, MemberSchema, HistorySchema
from models.books import Book
from models.librarian import Librarian
from models.member import Member
from models.history import History

# with app.app_context():
#     db.create_all()

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Library Management System"}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    if role == 'librarian':
        librarian = Librarian(username=username, password=password)
        db.session.add(librarian)
    elif role == 'member':
        member = Member(username=username, password=password)
        db.session.add(member)
    db.session.commit()
    return jsonify({"success": 200})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data['role'] == 'librarian':
        librarian = Librarian.query.filter_by(username=data['username'], password=data['password']).first()
        if librarian:
            access_token = create_access_token(identity={'username': librarian.username, 'role': 'librarian'})
            return jsonify({"access_token": access_token})
        else:
            return jsonify({"error": "Credentials didn't match"}), 401
    elif data['role'] == 'member':
        member = Member.query.filter_by(username=data['username'], password=data['password'], status="ACTIVE").first()
        if member:
            access_token = create_access_token(identity={'username': member.username, 'role': 'member'})
            return jsonify({"access_token": access_token})
        else:
            return jsonify({"error": "Credentials didn't match"}), 401
    else:
        return jsonify({"error": "Credentials didn't match"}), 401
    
@app.route('/viewbooks', methods=['GET'])
@jwt_required()
def viewbooks():
    token = get_jwt_identity()
    if token['role'] == 'librarian':
        books = Book.query.all()
        return jsonify(BookSchema(many=True).dump(books)), 200
    else:
        return jsonify({"error": 401}), 401
    
@app.route('/viewbook/<int:id>', methods=['GET'])
@jwt_required()
def viewbook(id):
    token = get_jwt_identity()
    if token['role'] == 'librarian':
        book = Book.query.get_or_404(id)
        return jsonify(BookSchema().dump(book)), 200
    else:
        return jsonify({"error": 401}), 401

@app.route('/addbooks', methods=['POST'])
@jwt_required()
def addbooks():
    token = get_jwt_identity()
    if token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        data = request.get_json()
        title = data.get('title')
        author = data.get('author')
        book = Book(title=title, author=author)
        db.session.add(book)
        db.session.commit()
        return jsonify({"success": f"{book} is added"}), 200
    else:
        return jsonify({"error": "Could not add book"}), 401

@app.route('/updatebook/<int:id>', methods=['PUT'])
@jwt_required()
def updatebook(id):
    token = get_jwt_identity()
    if token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        book = Book.query.get_or_404(id)
        data = request.get_json()
        book.title = data.get('title')
        book.author = data.get('author')
        db.session.commit()
        return jsonify({"success": f"{book} is updated"}), 200
    else:
        return jsonify({"error": "Could not update book"}), 401
    
@app.route('/deletebook/<int:id>', methods=['DELETE'])
@jwt_required()
def deletebook(id):
    token = get_jwt_identity()
    if token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        return jsonify({"success": f"{book} is deleted"}), 200
    else:
        return jsonify({"error": "Could not delete book"}), 401
    
@app.route('/borrowbook/<int:id>', methods=['POST'])
@jwt_required()
def borrowbook(id):
    token = get_jwt_identity()
    if token['role'] == 'member' and Member.query.filter_by(username=token['username']).first() is not None:
        book = Book.query.get_or_404(id)
        if book.status == "AVAILABLE":
            book.status = "BORROWED"
            book.borrewed_by = Member.query.filter_by(username=token['username']).first().id
            history = History(user_id=Member.query.filter_by(username=token['username']).first().id, book_id=id, action="BORROWED")
            db.session.add(history)
            db.session.commit()
            return jsonify({"success": f"{book} is borrowed"}), 200
        else:
            return jsonify({"error": "Book is not available"}), 401
    else:
        return jsonify({"error": "Could not borrow book"}), 401
    
@app.route('/returnbook/<int:id>', methods=['POST'])
@jwt_required()
def returnbook(id):
    token = get_jwt_identity()
    if token['role'] == 'member' and Member.query.filter_by(username=token['username']).first() is not None:
        book = Book.query.get_or_404(id)
        if book.status == "BORROWED" and book.borrewed_by == Member.query.filter_by(username=token['username']).first().id:
            book.status = "AVAILABLE"
            book.borrewed_by = None
            history = History(user_id=Member.query.filter_by(username=token['username']).first().id, book_id=id, action="RETURNED")
            db.session.add(history)
            db.session.commit()
            return jsonify({"success": f"{book} is returned"}), 200
        else:
            return jsonify({"error": "Book is not borrowed by you"}), 401
    else:
        return jsonify({"error": "Could not return book"}), 401
    
@app.route('/history', methods=['GET'])
@jwt_required()
def history():
    token = get_jwt_identity()
    if token['role'] == 'member' and Member.query.filter_by(username=token['username']).first() is not None:
        history = History.query.filter_by(user_id=Member.query.filter_by(username=token['username']).first().id).all()
        return jsonify({"history": history}), 200
    elif token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        history = History.query.all()
        return jsonify({"history": history}), 200
    else:
        return jsonify({"error": "Could not get history"}), 401
    
@app.route('/deletemember/<int:id>', methods=['DELETE'])
@jwt_required()
def deletemember_by_id(id):
    token = get_jwt_identity()
    if token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        user = Member.query.get_or_404(id)
        user.status = "INACTIVE"
        db.session.commit()
        return jsonify({"success": f"{user} is deleted"}), 200
    # elif token['role'] == 'member' and Member.query.filter_by(username=token['username']).first() is not None:
    #     user = Member.query.filter_by(username=token['username']).first()
    #     user.status = "INACTIVE"
    #     db.session.commit()
    #     return jsonify({"success": f"{user} is deleted"}), 200
    else:
        return jsonify({"error": "Could not delete user"}), 401
    
@app.route('/deletemember', methods=['DELETE'])
@jwt_required()
def deletemember():
    token = get_jwt_identity()
    if token['role'] == 'member' and Member.query.filter_by(username=token['username']).first() is not None:
        user = Member.query.filter_by(username=token['username']).first()
        user.status = "INACTIVE"
        db.session.commit()
        return jsonify({"success": f"{user} is deleted"}), 200
    else:
        return jsonify({"error": "Could not delete user"}), 401


@app.route('/updatemember/<int:id>', methods=['PUT'])
@jwt_required()
def updatemember(id):
    token = get_jwt_identity()
    if token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        data = request.get_json()
        user = Member.query.get_or_404(id)
        user.username = data['username']
        user.password = data['password']
        # user.status = data['status']
        db.session.commit()
        return jsonify({"success": f"{user} is updated"}), 200
    else:
        return jsonify({"error": "Could not update user"}), 401
    
@app.route('/viewmembers', methods=['GET'])
@jwt_required()
def viewmembers():
    token = get_jwt_identity()
    if token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        users = Member.query.all()
        return jsonify(MemberSchema(many=True).dump(users)), 200
    else:
        return jsonify({"error": "Could not get users"}), 401
    
@app.route('/viewmember/<int:id>', methods=['GET'])
@jwt_required()
def viewmember(id):
    token = get_jwt_identity()
    if token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        user = Member.query.get_or_404(id)
        return jsonify(MemberSchema().dump(user)), 200
    else:
        return jsonify({"error": "Could not get user"}), 401
    
@app.route('/addmember', methods=['POST'])
@jwt_required()
def addmember():
    token = get_jwt_identity()
    if token['role'] == 'librarian' and Librarian.query.filter_by(username=token['username']).first() is not None:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = Member(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"success": f"{user} is added"}), 200
    else:
        return jsonify({"error": "Could not add user"}), 401
# @app.route('/librarian')
# def librarian():
#     return render_template('librarian.html')

# @app.route('/member')
# def member():
#     return render_template('member.html')

# @app.route('/register')
# def register():
#     return render_template('register.html')

# @app.route('/register', methods=['GET','POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if request.form['role'] == 'librarian':
#             librarian = Librarian(username=username, password=password)
#             db.session.add(librarian)
#             db.session.commit()
#             return redirect(url_for('librarian'))
#         elif request.form['role'] == 'member':
#             member = Member(username=username, password=password)
#             db.session.add(member)
#             db.session.commit()
#             return redirect(url_for('member'))
#         # return jsonify({"username": username, "password": password, "role": request.form['role']})
#         # try:
#         #     db.session.commit()
#         #     return redirect(url_for(''))
#         # except Exception as e:
#         #     return f'There was an issue adding your task {e}'
#     else:
#         return render_template('register.html')
    # data = request.get_json()
    # username = data.get('username')
    # password = data.get('password')
    # role = data.get('role')
    
    # if role == 'librarian':
    #     librarian = Librarian(username=username, password=password)
    #     db.session.add(librarian)
    # elif role == 'member':
    #     member = Member(username=username, password=password)
    #     db.session.add(member)
    # db.session.commit()
    # return render_template('register.html')


# @app.route('/login', methods=['GET','POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         librarian = Librarian.query.filter_by(username=username, password=password).first()
#         # librarian_password = Librarian.query.filter_by(password=password).first()
#         member = Member.query.filter_by(username=username, password=password, status="ACTIVE").first()
#         # member_password = Member.query.filter_by(password=password).first()
#         if librarian:
#             access_token = create_access_token(identity={'username': librarian.username, 'role': 'librarian'})
#             # return redirect(url_for('librarian')), jsonify(access_token=access_token)
#             return jsonify({"access_token": access_token})
#         elif member:
#             return redirect(url_for('member'))
#         else:
#             return jsonify({"error": 401})

    # Create JWT token
    # access_token = create_access_token(identity={'username': user.username, 'role': user.role})
    # return jsonify({"success": 200})
    # return render_template('login.html')

# @app.route('/addbooks', methods=['GET','POST'])
# def books():
#     if request.method == 'POST':
#         title = request.form['title']
#         author = request.form['author']
#         book = Book(title=title, author=author)
#         db.session.add(book)
#         db.session.commit()
#         return redirect(url_for('librarian'))
#     else:
#         return render_template('addbooks.html')
#     # else:
#     #     books = Book.query.all()
#     #     return render_template('books.html', books=books)

# @app.route('/viewbooks', methods=['GET'])
# @jwt_required()
# def viewbooks():
#     token = get_jwt_identity()
#     if token['role'] == 'librarian':
#         books = Book.query.all()
#         return render_template('viewbooks.html', books=books)
#     else:
#         return jsonify({"error": 401})
#     # books = Book.query.all()
#     # return render_template('viewbooks.html', books=books)

# @app.route('/updatebook/<int:id>', methods=['GET','POST'])
# def updatebook(id):
#     book = Book.query.get_or_404(id)
#     if request.method == 'POST':
#         book.title = request.form['title']
#         book.author = request.form['author']
#         try:
#             db.session.commit()
#             return redirect('/viewbooks')
#         except Exception as e:
#             return f'There was an issue updating the book {e}'
#     else:
#         return render_template('updatebook.html', book=book)

# @app.route('/deletebook/<int:id>')
# def deletebook(id):
#     book = Book.query.get_or_404(id)
#     try:
#         db.session.delete(book)
#         db.session.commit()
#         return redirect('/viewbooks')
#     except Exception as e:
#         return f'There was an issue deleting the book {e}'

if __name__ == '__main__':
    app.run(debug=True)