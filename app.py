from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/sign_up')
def sign_up():
    return render_template('sign-up.html')

@app.route('/detail_content')
def detail_content():
    return render_template('detail-content.html')




if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)