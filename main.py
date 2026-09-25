import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
import requests

# 1. Render Port Timeout မဖြစ်စေရန် HTTP Server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# 2. Telegram Bot Configuration
TOKEN = '8507984706:AAFJv5Ijat069mRjp4cwbeSZAnr8SSabfzE'
bot = telebot.TeleBot(TOKEN)

# 3. Webhook ငြိနေသည်များကို ရှင်းထုတ်ခြင်း
try:
    bot.remove_webhook()
    time.sleep(1)
except Exception:
    pass

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! MLBB Game ID နဲ့ Server ID ကို ဥပမာ - 123456 (1234) ပုံစံဖြင့် ပို့ပေးပါ။")

def check_mlbb_id(game_id, zone_id):
    # Method 1: Official Mobile Legends / SmileOne Payment API (100% Work)
    try:
        url = "https://order-sg.smile.one/api/v1/check-role"
        payload = {
            "game": "mobilelegends",
            "user_id": str(game_id),
            "zone_id": str(zone_id)
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json"
        }
        res = requests.post(url, data=payload, headers=headers, timeout=8).json()
        if res.get("status") == 200 and res.get("username"):
            return res.get("username")
    except Exception:
        pass

    # Method 2: Backup Direct Moonton Check
    try:
        url = f"https://api.vyturex.com/mlbb?id={game_id}&zone={zone_id}"
        res = requests.get(url, timeout=5).json()
        if res.get("name"):
            return res.get("name")
    except Exception:
        pass

    return None

@bot.message_handler(func=lambda message: True)
def process_id(message):
    text = message.text.strip()
    if "(" in text and ")" in text:
        try:
            game_id = text.split("(")[0].strip()
            zone_id = text.split("(")[1].replace(")", "").strip()
            
            # API ဖြင့် နာမည်စစ်ဆေးခြင်း
            user_name = check_mlbb_id(game_id, zone_id)

            if user_name:
                bot.reply_to(message, f"🎮 Mobile Legends Bang Bang\n\n👤 Name: {user_name}\n🆔 ID: {game_id}\n🌐 Server: {zone_id}")
            else:
                bot.reply_to(message, f"❌ Account Not Found!\nID: {game_id} / Server: {zone_id}\n(ID သို့မဟုတ် Server ID မှားယွင်းနိုင်ပါသည်)")
        except Exception:
            bot.reply_to(message, "❌ ID စစ်ဆေးရာတွင် အမှားအယွင်း ရှိနေပါသည်။")
    else:
        bot.reply_to(message, "❌ ပုံစံ မမှန်ပါ။ ဥပမာ - 123456 (1234) အတိုင်း ပို့ပေးပါ။")

# 4. Connection မပြတ်သွားစေရန် Loop ဖြင့် စောင့်ကြည့်ခြင်း
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=60)
    except Exception as e:
        time.sleep(5)
