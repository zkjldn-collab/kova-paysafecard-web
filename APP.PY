from flask import Flask, request, render_template_string
import os
import requests

app = Flask(__name__)
DELAY_HOURS = 2
# ⚠️ ON METTRA L'ADRESSE DE TON BOT FPS.MS ICI PLUS TARD
BOT_WEBHOOK_URL = "http://37.148.199.201:10445/receive_order" 

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"><title>Paiement Paysafecard</title>
  <style>
    body { font-family: system-ui; max-width: 480px; margin: 80px auto; padding: 24px; background: #0f1115; color: #eee; }
    input { width: 100%; padding: 14px; font-size: 20px; letter-spacing: 3px; text-align: center; border-radius: 8px; border: 1px solid #333; background: #1a1d24; color: #fff; margin-top: 10px;}
    button { width: 100%; padding: 14px; margin-top: 16px; font-size: 16px; border-radius: 8px; border: 0; background: #2ecc71; color: #000; font-weight: 700; cursor: pointer; }
    .info { background: #1a1d24; padding: 14px; border-radius: 8px; margin-top: 20px; font-size: 14px; color: #aaa; }
  </style>
</head>
<body>
  <h1>💳 Paiement Paysafecard</h1>
  <form method="POST" action="/submit">
    <input type="hidden" name="invoice_id" value="{{ invoice_id }}">
    <label>Code PIN Paysafecard (16 chiffres) :</label>
    <input name="pin" maxlength="19" placeholder="1234 5678 9012 3456" required>
    <button type="submit">Envoyer mon code</button>
  </form>
  <div class="info">⏱️ Délai : {{ delay }}h max. Vérification manuelle.</div>
</body>
</html>
"""

@app.route("/checkout")
def checkout():
    invoice_id = request.args.get("invoice_id") or "INCONNU"
    return render_template_string(HTML, invoice_id=invoice_id, delay=DELAY_HOURS)

@app.route("/submit", methods=["POST"])
def submit():
    invoice_id = request.form["invoice_id"]
    pin = request.form["pin"].strip().replace("-", "").replace(" ", "")
    
    try:
        # On envoie le PIN au bot FPS.ms
        requests.post(BOT_WEBHOOK_URL, json={"invoice_id": invoice_id, "pin": pin})
    except Exception as e:
        return f"Erreur de connexion au bot : {e}", 500
        
    return "<h2 style='color:#2ecc71;text-align:center;margin-top:100px;font-family:sans-serif;'>✅ Code envoyé !<br>Ta commande sera validée sous peu.</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)