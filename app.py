from flask import Flask, render_template_string, request, jsonify
import datetime
import requests

app = Flask(__name__)

# -------------------------------------------------------------
# KONFIGURIMI I ABONIMIT DHE DATABASE-IT
# -------------------------------------------------------------
FIREBASE_URL = "https://sistemi-hyrjedalje-default-rtdb.firebaseio.com/"

# Data e skadimit të abonimit (VITI, MUAJI, DITA)
# E kam caktuar deri më 18 Nëntor 2026. Mund ta ndryshosh kur të duash!
DATA_E_SKADIMIT = datetime.date(2026, 11, 18)

def ka_skaduar_abonimi():
    sot = datetime.date.today()
    return sot > DATA_E_SKADIMIT
# -------------------------------------------------------------

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="sq">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistemi Hyrje-Dalje</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f6;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            justify-content: center;
            max-width: 1000px;
            width: 100%;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            width: 320px;
            text-align: center;
        }
        .dashboard {
            flex: 1;
            min-width: 320px;
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .expired-card {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            text-align: center;
            max-width: 450px;
            margin-top: 50px;
            border-top: 6px solid #dc3545;
        }
        h2, h3 { margin-top: 0; color: #333; }
        input {
            width: 90%;
            padding: 10px;
            margin-bottom: 12px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 15px;
        }
        .btn {
            width: 100%;
            padding: 12px;
            margin: 6px 0;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }
        .btn-entry { background-color: #28a745; color: white; }
        .btn-entry:hover { background-color: #218838; }
        .btn-exit { background-color: #dc3545; color: white; }
        .btn-exit:hover { background-color: #c82333; }
        .btn-refresh { background-color: #007bff; color: white; padding: 8px 15px; width: auto; margin-bottom: 15px; }
        .btn-refresh:hover { background-color: #0069d9; }
        #status { margin-top: 15px; font-weight: bold; }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }
        th { background-color: #f8f9fa; }
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-hyrje { background-color: #28a745; }
        .badge-dalje { background-color: #dc3545; }
    </style>
</head>
<body>

    {% if ka_skaduar %}
    <div class="expired-card">
        <h2 style="color: #dc3545;">⚠️ ABONIMI KA SKADUAR</h2>
        <p style="font-size: 16px; color: #555;">Afati i përdorimit të këtij sistemi ka përfunduar.</p>
        <p style="font-weight: bold; color: #333;">Ju lutem kontaktoni zhvilluesin për rinovimin e licencës/abonimit.</p>
    </div>
    {% else %}
    <div class="container">
        <!-- Forma e Regjistrimit -->
        <div class="card">
            <h2>Hyrje / Dalje</h2>
            <input type="text" id="emri" placeholder="Shkruaj emrin..." />
            <button class="btn btn-entry" onclick="dergoRegjistrim('Hyrje')">🟢 Regjistro HYRJE</button>
            <button class="btn btn-exit" onclick="dergoRegjistrim('Dalje')">🔴 Regjistro DALJE</button>
            <div id="status"></div>
        </div>

        <!-- Tabela e Dashboard-it -->
        <div class="dashboard">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>Lista e Regjistrimeve (Live)</h3>
                <button class="btn btn-refresh" onclick="marrRegjistrimet()">🔄 Rifresko</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Emri</th>
                        <th>Lloji</th>
                        <th>Koha</th>
                    </tr>
                </thead>
                <tbody id="tabela-trup">
                    <tr><td colspan="3">Po ngarkohen të dhënat...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function dergoRegjistrim(tipi) {
            const emri = document.getElementById('emri').value.trim();
            const statusDiv = document.getElementById('status');
            
            if (!emri) {
                statusDiv.style.color = 'red';
                statusDiv.innerText = 'Ju lutem shkruani emrin!';
                return;
            }

            fetch('/regjistro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emri: emri, tipi: tipi })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'expired') {
                    alert(data.mesazhi);
                    location.reload();
                    return;
                }
                statusDiv.style.color = 'green';
                statusDiv.innerText = data.mesazhi;
                marrRegjistrimet();
            })
            .catch(err => {
                statusDiv.style.color = 'red';
                statusDiv.innerText = 'Gabim gjatë dërgimit!';
            });
        }

        function marrRegjistrimet() {
            fetch('/lexo-regjistrimet')
            .then(res => res.json())
            .then(data => {
                const trup = document.getElementById('tabela-trup');
                trup.innerHTML = '';
                
                if (!data || Object.keys(data).length === 0) {
                    trup.innerHTML = '<tr><td colspan="3">Nuk ka asnjë regjistrim.</td></tr>';
                    return;
                }

                const lista = Object.values(data).reverse();
                lista.forEach(r => {
                    const klasaBadge = r.tipi === 'Hyrje' ? 'badge-hyrje' : 'badge-dalje';
                    trup.innerHTML += `
                        <tr>
                            <td><b>${r.emri}</b></td>
                            <td><span class="badge ${klasaBadge}">${r.tipi}</span></td>
                            <td>${r.koha}</td>
                        </tr>
                    `;
                });
            });
        }

        marrRegjistrimet();
    </script>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def home():
    skaduar = ka_skaduar_abonimi()
    return render_template_string(HTML_TEMPLATE, ka_skaduar=skaduar)

@app.route('/regjistro', methods=['POST'])
def regjistro():
    if ka_skaduar_abonimi():
        return jsonify({"status": "expired", "mesazhi": "Abonimi ka skaduar! Kontaktoni administratorin."})

    data = request.get_json()
    emri = data.get('emri')
    tipi = data.get('tipi')
    koha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    regjistrimi = {
        "emri": emri,
        "tipi": tipi,
        "koha": koha
    }
    
    response = requests.post(f"{FIREBASE_URL}/regjistrimet.json", json=regjistrimi)
    
    if response.status_code == 200:
        return jsonify({"status": "success", "mesazhi": f"{tipi} u regjistrua me sukses!"})
    else:
        return jsonify({"status": "error", "mesazhi": "Dështoi ruajtja në Cloud."})

@app.route('/lexo-regjistrimet', methods=['GET'])
def lexo_regjistrimet():
    if ka_skaduar_abonimi():
        return jsonify({})

    response = requests.get(f"{FIREBASE_URL}/regjistrimet.json")
    if response.status_code == 200:
        return jsonify(response.json() or {})
    return jsonify({})

if __name__ == '__main__':
    app.run(port=5000, debug=True)