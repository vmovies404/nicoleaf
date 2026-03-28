from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime

import os, random

app = Flask(__name__)
app.config["SECRET_KEY"] = "nicoleaf-secret-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nicoleaf.db"
app.config["UPLOAD_FOLDER"] = "static/uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db = SQLAlchemy(app)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=False)
    nicotine_level = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def estimate_nicotine_level(image_path):
    return round(random.uniform(1.0, 5.0), 2)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            nicotine = estimate_nicotine_level(filepath)
            entry = Analysis(image_filename=filename, nicotine_level=nicotine)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("result", id=entry.id))
    return render_template("index.html")

@app.route("/result/<int:id>")
def result(id):
    analysis = Analysis.query.get_or_404(id)
    image_url = url_for("static", filename=f"uploads/{analysis.image_filename}")
    return render_template("result.html", analysis=analysis, image_url=image_url)

@app.route("/history")
def history():
    analyses = Analysis.query.order_by(Analysis.timestamp.desc()).all()
    return render_template("history.html", analyses=analyses)

@app.route("/static/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/delete/<int:id>")
def delete(id):
    entry = Analysis.query.get_or_404(id)

    # delete image file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], entry.image_filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for("history"))

app.run(debug=True, port=5000)
