from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
import locale
import jwt
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

SECRET_KEY = "DJOURNEY"

MONGODB_CONNECTION_STRING = "mongodb+srv://iffahrisma12:sparta@cluster0.ntlxsm9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbjourney

TOKEN_KEY = "mytoken"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/auth_login')
def auth_login():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        data_user = {
            'profilename': user_info['profile_name'],
            'level': user_info['level']
        }
        return jsonify({"result": "success", "data": data_user})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})

@app.route('/login')
def page_login():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})

        print(user_info)

        return redirect(url_for("home", msg="Anda sudah login!"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('login.html')
    


@app.route('/register/check_dup', methods=["POST"])
def check_dup():
    username_receive = request.form.get("username_give")
    exists = bool(db.user.find_one({'username': username_receive}))
    return jsonify({"result": "success", "exists": exists})


@app.route('/register', methods=["POST"])
def register():
    username_receive = request.form.get("username_give")
    email_receive = request.form.get("email_give")
    password_receive = request.form.get("password_give")

    data_user = {
        "username": username_receive,
        "email": email_receive,
        "password": password_receive,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_icon.png",
        "profile_info": "",
        "blocked": False,
        "level": 2
    }

    db.user.insert_one(data_user)

    return jsonify({"result": "success", "data": email_receive})


@app.route('/login', methods=["POST"])
def login():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]

    result = db.user.find_one(
        {
            "email": email_receive,
            "password": password_receive,
        }
    )

    data_user = {
        'profilename': result['profile_name'],
        'level': result['level']
    }

    if result:
        payload = {
            "id": result['username'],
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
                "data":data_user,
            }
        )
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "Kami tidak dapat menemukan akun anda, silakan cek email dan password anda!",
            }
        )
    
@app.route("/post_story", methods=["POST"])
def posting():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        username = user_info["username"]
        judul_receive = request.form["judul_give"]
        lokasi_receive = request.form["lokasi_give"]
        deskripsi_receive = request.form["deskripsi_give"]
        date_receive = request.form["date_give"]
        if "file_give" in request.files:
            time = datetime.now().strftime("%m%d%H%M%S")
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"img_post/postimg-{username}-{time}.{extension}"
            file.save("./static/" + file_path)
        doc = {
            "postid": f"postid-{username}-{time}",
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "judul": judul_receive,
            "lokasi": lokasi_receive,
            "deskripsi": deskripsi_receive,
            "image": file_path,
            "date": date_receive,
            "confirm":0
        }

        db.posts.insert_one(doc)
        return jsonify({"result": "success", "msg": f'Postingan dengan judul "{judul_receive}" berhasil dikirim! Silakan tunggu konfirmasi dari admin!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/update_story", methods=["POST"])
def update_post():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        username = user_info["username"]
        id_receive = request.form['id_give']
        judul_receive = request.form["judul_give"]
        lokasi_receive = request.form["lokasi_give"]
        deskripsi_receive = request.form["deskripsi_give"]
        new_doc = {
            "judul": judul_receive,
            "lokasi": lokasi_receive,
            "deskripsi": deskripsi_receive
        }
        if "file_give" in request.files:
            time = datetime.now().strftime("%m%d%H%M%S")
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"img_post/postimg-{username}-{time}.{extension}"
            file.save("./static/" + file_path)
            new_doc["image"] = file_path

        db.posts.update_one({"postid": id_receive}, {"$set": new_doc})
        return jsonify({"result": "success", "msg": f'Postingan dengan judul "{judul_receive}" berhasil diupdate!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    
@app.route('/delete/<idpost>', methods=['POST'])
def delete(idpost):
    db.posts.delete_one({"postid":idpost})
    return jsonify({"result": "success", "msg": "Postingan berhasil dihapus!"})

@app.route("/list_post")
def get_posts():
    posts = list(db.posts.find({}).sort("date", -1).limit(20))
    for post in posts:
        post["_id"] = str(post["_id"])

    return jsonify({"result": "success", "msg": "Successful fetched all posts", "posts": posts})


@app.route('/detail_content/<idpost>')
def detail_content(idpost):
    try:
        post_info = db.posts.find_one(
                {"postid": idpost},
                {"_id": False}
            )
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF8')

        date_string = post_info['date']
        date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        date = date_object.date()
        formatted_date = date.strftime("%d %B %Y")

        return render_template("detail-content.html", post_info=post_info, datepost=formatted_date)
    except:
        return redirect(url_for("content",  errmsg="Postingan ini tidak ada atau sudah dihapus!"))


@app.route('/content')
def content():
    return render_template('content.html')


@app.route('/media')
def media():
    return render_template('media.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/detail_content')
def detail_content_sample():
    return render_template('detail-content.html')


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
