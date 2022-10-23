from flask import Flask, render_template

Appli = Flask(__name__)


@Appli.route('/')
def home():
    return render_template('html/Home.html')

@Appli.route('/Signin')
def login():
    return render_template('html/Signin.html')


@Appli.route('/Signup')
def Registration():
    return render_template('html/Signup.html')


@Appli.route('/About')
def about():
    return render_template('html/About.html')


if __name__ == '__main__':
    Appli.run()
