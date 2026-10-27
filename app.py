from flask import Flask, request, render_template_string
import os
import requests

app = Flask(__name__)
DELAY_HOURS = 2
BOT_WEBHOOK_URL = os.environ.get("BOT_WEBHOOK_URL", "http://37.148.199.201:10445/receive_order")

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"><title>Paiement Paysafecard - KovaShop</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; background: #0a0a0c; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .card { background: #14151a; border: 1px solid #2a2b33; border-radius: 16px; width: 100%; max-width: 440px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
    .header img { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; }
    .header h1 { font-size: 20px; margin: 0; font-weight: 600; }
    .header p { margin: 4px 0 0; font-size: 13px; color: #888; }
    .price { font-size: 24px; font-weight: 700; color: #2ecc71; margin-bottom: 24px; }
    .input-group { margin-bottom: 20px; }
    .input-group label { display: block; font-size: 13px; color: #aaa; margin-bottom: 8px; font-weight: 600; }
    input { width: 100%; padding: 16px; font-size: 18px; letter-spacing: 4px; text-align: center; border-radius: 10px; border: 1px solid #333; background: #0f1115; color: #fff; box-sizing: border-box; transition: border 0.3s; }
    input:focus { outline: none; border-color: #2ecc71; }
    button { width: 100%; padding: 16px; font-size: 16px; font-weight: 600; border-radius: 10px; border: 0; background: #2ecc71; color: #000; cursor: pointer; transition: background 0.3s; }
    button:hover { background: #27ae60; }
    .info { background: rgba(46, 204, 113, 0.1); border: 1px solid rgba(46, 204, 113, 0.2); padding: 16px; border-radius: 10px; margin-top: 24px; font-size: 13px; color: #2ecc71; text-align: center; }
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div>
        <h1>Paiement Paysafecard</h1>
        <p>Commande sécurisée sur KovaShop</p>
      </div>
    </div>
    
    <div class="price">Montant : {{ amount }} €</div>

    <form method="POST" action="/submit">
      <input type="hidden" name="invoice_id" value="{{ invoice_id }}">
      <input type="hidden" name="amount" value="{{ amount }}">
      
      <div class="input-group">
        <label>Code PIN Paysafecard (16 chiffres)</label>
        <input name="pin" maxlength="19" placeholder="1234 5678 9012 3456" required autofocus>
      </div>
      
      <button type="submit">Envoyer mon code</button>
    </form>

    <div class="info">
      ⏱️ Délai de traitement : <strong>{{ delay }}h maximum</strong>.<br>
      Vérification manuelle avant livraison.
    </div>
  </div>
</body>
</html>
"""

@app.route("/checkout")
def checkout():
    # SellAuth envoie l'ID de facture et le montant dans l'URL
    invoice_id = request.args.get("invoice_id") or request.args.get("invoice") or "INCONNU"
    amount = request.args.get("amount") or request.args.get("price") or "0.00"
    return render_template_string(HTML, invoice_id=invoice_id, amount=amount, delay=DELAY_HOURS)

@app.route("/submit", methods=["POST"])
def submit():
    invoice_id = request.form["invoice_id"]
    pin = request.form["pin"].strip().replace("-", "").replace(" ", "")
    amount = request.form.get("amount", "0.00")
    
    try:
        requests.post(BOT_WEBHOOK_URL, json={"invoice_id": invoice_id, "pin": pin, "amount": amount}, timeout=10)
    except Exception as e:
        return f"Erreur de connexion au bot : {e}", 500
        
    return "<h2 style='color:#2ecc71;text-align:center;margin-top:100px;font-family:sans-serif;'>✅ Code envoyé !<br>Ta commande sera validée sous peu.</h2>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
