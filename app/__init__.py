from flask import Blueprint, render_template

main = Blueprint("main", __name__)

# 🏠 HOME


@main.route("/")
def home():
    return render_template("home.html")

# 📚 BLOG


@main.route("/blog")
def blog():
    return render_template("blog.html")
