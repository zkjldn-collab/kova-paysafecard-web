from flask import Flask, request, render_template_string
import os
import sqlite3

app = Flask(__name__)
DELAY_HOURS = 2

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
  <meta charset="UTF-8">
  <title>Paiement Paysafecard - KovaShop</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { 
        font-family: 'Inter', sans-serif; 
        color: #fff; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        min-height: 100vh; 
        background: #0a0a0c;
        background-image: url('https://i.imgur.com/I2mKawk.png');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    body::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(10, 10, 12, 0.75);
        z-index: -1;
    }

    .card { 
        background: rgba(20, 21, 26, 0.85);
        backdrop-filter: blur(12px); 
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 20px; 
        width: 100%; 
        max-width: 440px; 
        padding: 40px; 
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        text-align: center;
    }

    .logo { 
        width: 90px; 
        height: 90px; 
        border-radius: 50%; 
        object-fit: cover; 
        margin-bottom: 15px;
        border: 2px solid #f1c40f;
        box-shadow: 0 0 25px rgba(241, 196, 15, 0.4);
    }

    h1 { font-size: 24px; font-weight: 800; margin-bottom: 5px; color: #fff; }
    .subtitle { font-size: 13px; color: #aaa; margin-bottom: 25px; }
    
    .price-tag { 
        font-size: 32px; 
        font-weight: 800; 
        color: #f1c40f; 
        margin-bottom: 30px;
        text-shadow: 0 0 15px rgba(241, 196, 15, 0.4);
    }

    label { display: block; font-size: 13px; color: #ccc; margin-bottom: 10px; text-align: left; font-weight: 600; }
    
    input { 
        width: 100%; 
        padding: 16px; 
        font-size: 20px; 
        letter-spacing: 5px; 
        text-align: center; 
        border-radius: 12px; 
        border: 2px solid #333; 
        background: rgba(0,0,0,0.5); 
        color: #fff; 
        margin-bottom: 20px; 
        transition: all 0.3s;
    }
    input:focus { outline: none; border-color: #f1c40f; box-shadow: 0 0 10px rgba(241, 196, 15, 0.2); }
    
    button { 
        width: 100%; 
        padding: 16px; 
        font-size: 16px; 
        font-weight: 800; 
        border-radius: 12px; 
        border: 0; 
        background: linear-gradient(135deg, #f1c40f, #e67e22); 
        color: #000; 
        cursor: pointer; 
        transition: transform 0.2s, box-shadow 0.2s;
    }
    button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(241, 196, 15, 0.3); }
    
    .info { 
        background: rgba(255, 255, 255, 0.05); 
        border-left: 4px solid #f1c40f; 
        padding: 15px; 
        border-radius: 8px; 
        margin-top: 30px; 
        font-size: 13px; 
        color: #ccc; 
        text-align: left;
    }
    .info strong { color: #fff; }
  </style>
</head>
<body>
  <div class="card">
    <!-- Ton logo KovaShop -->
    <img src="https://i.imgur.com/I2mKawk.png" class="logo" alt="KovaShop">
    
    <h1>Paiement Paysafecard</h1>
    <p class="subtitle">Commande sécurisée sur KovaShop</p>
    
    <div class="price-tag">{{ amount }} €</div>

    <form method="POST" action="/submit">
      <input type="hidden" name="invoice_id" value="{{ invoice_id }}">
      <input type="hidden" name="amount" value="{{ amount }}">
      
      <label>Code PIN Paysafecard (16 chiffres)</label>
      <input name="pin" maxlength="19" placeholder="1234 5678 9012 3456" required autofocus>
      
      <button type="submit">Envoyer mon code</button>
    </form>

    <div class="info">
      ⏱️ <strong>Délai de traitement : {{ delay }}h max.</strong><br>
      Vérification manuelle avant livraison. Support disponible 24h/24 sur notre Discord.
    </div>
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
    
    con = sqlite3.connect("render_data.db")
    con.execute("INSERT OR REPLACE INTO orders (invoice_id, pin, amount) VALUES (?, ?, ?)", (invoice_id, pin, amount))
    con.commit()
    con.close()
        
    return """
    <div style="display:flex; justify-content:center; align-items:center; height:100vh; background:#0a0a0c; color:#f1c40f; font-family:sans-serif; text-align:center;">
        <div>
            <h1 style="font-size:40px;">✅ Code envoyé !</h1>
            <p style="color:#fff; font-size:18px;">Ta commande est en cours de vérification.<br>Elle sera validée sous peu.</p>
        </div>
    </div>
    """

@app.route("/api/orders")
def api_orders():
    con = sqlite3.connect("render_data.db")
    rows = con.execute("SELECT invoice_id, pin, amount FROM orders").fetchall()
    con.close()
    return {"orders": [{"invoice_id": r[0], "pin": r[1], "amount": r[2]} for r in rows]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
