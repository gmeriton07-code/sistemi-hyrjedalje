from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "rendesishumee_geheime_sleutel"

# Hardcoded verifikimi i abonimit (skadon më 2026-11-18)
EXPIRE_DATE = datetime(2026, 11, 18)

@app.before_request
def check_subscription():
    if datetime.now() > EXPIRE_DATE:
        return "<h1>Abonimi ka skaduar. Ju lutem kontaktoni administratorin.</h1>", 403

# Lista ku ruhen përkohësisht punëtorët me email
workers_list = []

@app.route('/')
def home():
    return render_template('index.html', workers=workers_list)

@app.route('/regjistro', methods=['POST'])
def regjistro():
    emri = request.form.get('emri')
    email = request.form.get('email')
    
    if emri and email:
        workers_list.append({"emri": emri, "email": email})
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
