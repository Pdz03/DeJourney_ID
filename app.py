from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
import jwt


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

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
        user_info = db.user.find_one({'email': payload.get('id')})
        data_user = {
            'username': user_info['profile_name'],
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
        user_info = db.user.find_one({'email': payload.get('id')})

        print(user_info)

        return redirect(url_for("home", msg="Anda sudah login!"))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('login.html')
    


@app.route('/register/check_dup', methods=["POST"])
def check_dup():
    username_receive = request.form.get("username_give")
    exists = bool(db.user.find_one({'username': username_receive}))
    # hash = "admin123"

    # doc = [
    #     {"username": "admin1",
    #      "email": "admin1@dejourney.id",
    #      "password": hash,
    #      "profile_name": "admin1",
    #      "profile_pic": "",
    #      "profile_pic_real": "profile_pics/profile_icon.png",
    #      "profile_info": "",
    #      "blocked": False,
    #      "level": 1
    #      },
    #     {"username": "admin2",
    #      "email": "admin2@dejourney.id",
    #      "password": hash,
    #      "profile_name": "admin2",
    #      "profile_pic": "",
    #      "profile_pic_real": "profile_pics/profile_icon.png",
    #      "profile_info": "",
    #      "blocked": False,
    #      "level": 1
    #      },
    #     {"username": "admin3",
    #      "email": "admin3@dejourney.id",
    #      "password": hash,
    #      "profile_name": "admin3",
    #      "profile_pic": "",
    #      "profile_pic_real": "profile_pics/profile_icon.png",
    #      "profile_info": "",
    #      "blocked": False,
    #      "level": 1
    #      }
    # ]

    # db.user.insert_many(doc)
    # listuser = list(db.user.find({},{'_id':False}))
    # print(listuser)

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
        'username': result['profile_name'],
        'level': result['level']
    }

    if result:
        payload = {
            "id": email_receive,
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


@app.route('/content')
def content():
    return render_template('content.html', nav_active="content")


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
def detail_content():
    return render_template('detail-content.html')


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
