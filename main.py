from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    db.relationship("Comment", backref="thread")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey("thread.id"))
    content = db.Column(db.String(1024))

# CORS許可
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/thread", methods=["GET", "POST", "DELETE"])
def thread():

    if request.method == "GET":
        if request.args.get("id") != None:
            threads = db.session.query(Thread.id, Thread.name)\
                .filter(Thread.id==request.args.get("id"))\
                .all()
        else:
            threads = db.session.query(Thread.id, Thread.name)\
                .all()
        
        threads = [{"id": t.id, "name": t.name} for t in threads]
        return jsonify({"threads": threads})

    elif request.method == "POST":
        if request.json.get("name") == None:
            return "Failed"
        new_thread = Thread(name=request.json.get("name"))
        db.session.add(new_thread)
        db.session.commit()
        return "SUCCESS"
    
    else:
        db.session.query(Thread)\
            .filter(Thread.id==request.json.get("id"))\
            .delete()
        
        # スレのコメントも削除
        db.session.query(Comment)\
            .filter(Comment.thread_id==request.json.get("id"))\
            .delete()
        db.session.commit()
        return "SUCCESS"


@app.route("/comment/thread/<thread_id>", methods=["GET"])
def get_thread_comments(thread_id):
    comments = db.session.query(Comment.id, Comment.thread_id, Comment.content)\
        .filter(Comment.thread_id==thread_id)\
        .all()
    comments = [{"id": c.id, "thread_id": c.thread_id, "content": c.content} for c in comments]
    
    return jsonify({"comments": comments})


@app.route("/comment", methods=["POST"])
def post_comment():
    print("DEBUG==========")
    print(request.json)

    thread_id = request.json.get("thread_id")
    content = request.json.get("content")
    
    q = db.session.query(Thread).filter(Thread.id==thread_id)
    if not db.session.query(q.exists()).scalar():
        return "No threads found"
    
    new_comment = Comment(thread_id=thread_id, content=content)
    db.session.add(new_comment)
    db.session.commit()
    return "SUCCESS"
    

@app.route("/comment/<_id>", methods=["DELETE"])
def delete_comment(_id):

    db.session.query(Comment)\
        .filter(Comment.id==_id)\
        .delete()
    db.session.commit()
    return "SUCCESS"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
