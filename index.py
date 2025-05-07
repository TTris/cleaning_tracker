from flask import Flask, render_template
from api.locations import locations_bp
from api.records import records_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.register_blueprint(locations_bp)
app.register_blueprint(records_bp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

# 本地開發使用，部署vercel時會被忽略
if __name__ == "__main__":
    app.run(debug=True)