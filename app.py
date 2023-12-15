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
    kategori = list(db.categories.find({}))
    media = list(db.media.find({}))
    return render_template('index.html', kategori=kategori, media=media)


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
        print(user_info)
        data_user = {
            'username': user_info['username'],
            'profilename': user_info['profile_name'],
            'level': user_info['level'],
            'profile_icon': user_info['profile_pic_real']
        }
        return jsonify({"result": "success", "data": data_user})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@app.route('/auth_login/<postcreator>')
def auth_login_detail(postcreator):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        if user_info['username'] == postcreator:
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@app.route('/auth_login/<commentcreator>')
def auth_login_comment(commentcreator):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        user_info = db.user.find_one({'username': payload.get('id')})
        if user_info['username'] == commentcreator:
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail"})
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
                "data": data_user,
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
            "confirm": 0
        }

        db.posts.insert_one(doc)
        return jsonify({"result": "success", "msg": f'Postingan dengan judul "{judul_receive}" berhasil dikirim! Silakan tunggu konfirmasi dari admin!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/update_like", methods=["POST"])
def update_like():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # We should change the like count for the post here
        user_info = db.user.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "postid": post_id_receive,
            "username": user_info["username"],
            "type": type_receive,
        }

        print(action_receive)

        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents(
            {"postid": post_id_receive, "type": type_receive}
        )

        return jsonify({"result": "success", "msg": "updated", "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/add_comment", methods=["POST"])
def add_comment():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # We should change the like count for the post here
        user_info = db.user.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        comment_receive = request.form["comment_give"]
        time = datetime.now().strftime("%m%d%H%M%S")
        date_receive = request.form["date_give"]
        doc = {
            "commentid": f'commentid-{time}',
            "postid": post_id_receive,
            "username": user_info["username"],
            "comment": comment_receive,
            "date": date_receive
        }

        db.comments.insert_one(doc)
        count = db.comments.count_documents(
            {"postid": post_id_receive}
        )

        return jsonify({"result": "success", "msg": "Komentar terkirim!", "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/update_comment", methods=["POST"])
def update_comment():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        comment_id_receive = request.form["comment_id_give"]
        comment_receive = request.form["comment_give"]

        db.comments.update_one({"commentid": comment_id_receive}, {
                               "$set": {"comment": comment_receive}})
        return jsonify({"result": "success", "msg": "Komentar sukses diupdate!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/deletecomment/<idcomment>', methods=['POST'])
def deletecomment(idcomment):
    db.comments.delete_one({"commentid": idcomment})
    return jsonify({"result": "success", "msg": "Komentar berhasil dihapus!"})


@app.route("/update_reply/<commentid>", methods=["POST"])
def update_reply(commentid):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        # We should change the like count for the post here
        user_info = db.user.find_one({"username": payload["id"]})
        commentid_receive = request.form["commentid_give"]
        reply_receive = request.form["reply_give"]
        date_receive = request.form["date_give"]
        doc = {
            "commentid": commentid_receive,
            "username": user_info["username"],
            "reply": reply_receive,
            "date": date_receive,
        }

        db.comments.insert_one(doc)
        count = db.comments.count_documents(
            {"postid": post_id_receive}
        )

        return jsonify({"result": "success", "msg": "updated", "count": count})
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
    db.posts.delete_one({"postid": idpost})
    return jsonify({"result": "success", "msg": "Postingan berhasil dihapus!"})


@app.route("/list_post")
def get_posts():
    posts = list(db.posts.find({}).sort("date", -1).limit(20))
    for post in posts:
        post["_id"] = str(post["_id"])

    return jsonify({"result": "success", "msg": "Successful fetched all posts", "posts": posts})


@app.route('/detail_content/<idpost>')
def detail_content(idpost):
    token_receive = request.cookies.get("mytoken")
    post_info = db.posts.find_one(
        {"postid": idpost},
        {"_id": False}
    )
    print(post_info)
    if post_info != None:
        post_info["count_heart"] = db.likes.count_documents(
            {"postid": idpost, "type": "heart"})
        post_info['count_comment'] = db.comments.count_documents(
            {"postid": idpost})

        date_string_post = post_info['date']
        date_object = datetime.strptime(
            date_string_post, "%Y-%m-%dT%H:%M:%S.%fZ")
        date = date_object.date()
        formatted_date = date.strftime("%d %B %Y")

        user = db.user.find_one({"username": post_info['username']})

    komen_info = list(db.comments.find({"postid": idpost}).sort("date", -1))
    for komen in komen_info:
        komen["_id"] = str(komen["_id"])
        komen['user'] = db.user.find_one({"username": komen['username']})
        date_string_komen = komen['date']
        date_object_komen = datetime.strptime(
            date_string_komen, "%Y-%m-%dT%H:%M:%S.%fZ")
        now = datetime.now()
        difference = now - date_object_komen
        seconds_difference = difference.total_seconds()
        minutes_difference = (seconds_difference / 60)
        hours_difference = (seconds_difference / 3600)
        days_difference = (hours_difference / 24)

        if minutes_difference < 1:
            formatted_difference = "Just now"
        elif minutes_difference < 2:
            formatted_difference = "1 minute ago"
        elif minutes_difference < 60:
            formatted_difference = f"{int(minutes_difference)} minutes ago"
        elif hours_difference < 2:
            formatted_difference = "1 hour ago"
        elif hours_difference < 24:
            formatted_difference = f"{int(hours_difference)} hours ago"
        elif days_difference < 2:
            formatted_difference = "1 day ago"
        elif days_difference < 7:
            formatted_difference = f"{int(days_difference)}1 day ago"
        else:
            formatted_difference = date_object_komen.date().strftime("%d %B %Y")
        komen['timecom'] = formatted_difference

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        post_info["heart_by_me"] = bool(db.likes.find_one(
            {"postid": idpost, "type": "heart", "username": payload['id']}))

        user_info = db.user.find_one({"username": payload["id"]})

        return render_template(
            "detail-content.html",
            post_info=post_info,
            datepost=formatted_date,
            user=user,
            user_info=user_info,
            komen_info=komen_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        if post_info != None:
            return render_template(
                "detail-content.html",
                post_info=post_info,
                datepost=formatted_date,
                user=user,
                komen_info=komen_info
            )
        elif post_info == None:
            return redirect(url_for("content",  errmsg="Postingan ini tidak ada atau sudah dihapus!"))


@app.route('/user/<username>')
def user(username):
    user_info = db.user.find_one(
        {"username": username},
        {"_id": False}
    )
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})
        print(user_login)
        if user_info['username'] == user_login['username']:
            return render_template("user-profile.html", user_info=user_info, user_login=user_login)
        else:
            return render_template("user-profile.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("user-profile.html", user_info=user_info)


@app.route("/update_profile", methods=["POST"])
def update_profile():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        fullname_receive = request.form["fullname_give"]
        email_receive = request.form["email_give"]
        job_receive = request.form["job_give"]
        phone_receive = request.form["phone_give"]
        address_receive = request.form["address_give"]
        bio_receive = request.form["bio_give"]
        new_doc = {
            "profile_name": fullname_receive,
            "email": email_receive,
            "profile_job": job_receive,
            "profile_phone": phone_receive,
            "profile_address": address_receive,
            "profile_info": bio_receive
        }
        if "file_give" in request.files:
            time = datetime.now().strftime("%m%d%H%M%S")
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/profilimg-{username}-{time}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.user.update_one({"username": payload["id"]}, {"$set": new_doc})
        return jsonify({"result": "success", "msg": "Profile updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/confirm_post', methods=["POST"])
def confirm_post():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        id_receive = request.form["id_give"]
        type_receive = request.form["type_give"]
        db.posts.update_one({"postid": id_receive}, {
                            "$set": {'confirm': int(type_receive)}})
        return jsonify({"result": "success", "msg": "Post updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("dashboard"))


@app.route('/content')
def content():
    return render_template('content.html')

@app.route('/cate', methods=['POST'])
def cate():
    doc = [
        {'kategori':'Pantai'},
        {'kategori':'Gunung'},
        {'kategori':'Taman'},
        {'kategori':'Danau'}
    ]

    print(doc)
    db.categories.insert_many(doc)
    return jsonify({"result": "success", "msg": "Post updated!"})


@app.route('/media')
def media():
    kategori = list(db.categories.find({}))
    media = list(db.media.find({}))
    print(media)
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})
        return render_template('media.html', kategori=kategori, user_login=user_login, media=media)
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('media.html', kategori=kategori, media=media)

@app.route('/add_media', methods=['POST'])
def add_media():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})

        title_receive = request.form["title_give"]
        kategori_receive = request.form["kategori_give"]
        type_receive = request.form["type_give"]
        deskripsi_receive = request.form["deskripsi_give"]
        doc = {
            'username': user_login['username'],
            'title': title_receive,
            'kategori': kategori_receive,
            'deskripsi': deskripsi_receive
        }
        if "file_give" in request.files:
            time = datetime.now().strftime("%m%d%H%M%S")
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"img_media/mediaimg-{user_login['username']}-{time}.{extension}"
            file.save("./static/" + file_path)
            doc["image"] = file_path
        if type_receive == 'baru':
            db.categories.insert_one({'kategori':kategori_receive})
        print(doc)
        db.media.insert_one(doc)
        return jsonify({"result": "success", "msg": "Post updated!"})
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("media"))


@app.route('/about')
def about():
    token_receive = request.cookies.get("mytoken")
    data = list(db.saran.find({}))
    print(data)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_login = db.user.find_one({"username": payload["id"]})
        return render_template('about.html', user_login=user_login, datasaran=data)
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('about.html', datasaran=data)
    
@app.route('/post_saran', methods=['POST'])
def post_saran():
    username_receive = request.form['username_give']
    message_receive = request.form['message_give']
    doc= {
        'username': username_receive,
        'message': message_receive,
        'show': False
    }
    db.saran.insert_one(doc)
    return jsonify({"result": "success", "msg": "Saran terkirim!"})


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/detail_content')
def detail_content_sample():
    return render_template('detail-content.html')


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
