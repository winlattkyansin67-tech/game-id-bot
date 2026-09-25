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

@bot.message_handler(func=lambda message: True)
def check_id(message):
    text = message.text.strip()
    if "(" in text and ")" in text:
        try:
            game_id = text.split("(")[0].strip()
            zone_id = text.split("(")[1].replace(")", "").strip()
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            user_name = None

            # API 1
            try:
                url1 = f"https://api.vyturex.com/mlbb?id={game_id}&zone={zone_id}"
                r1 = requests.get(url1, headers=headers, timeout=5).json()
                if "name" in r1 and r1["name"]:
                    user_name = r1["name"]
            except Exception:
                pass

            # API 2 (Backup)
            if not user_name:
                try:
                    url2 = f"https://api.eliasn.my.id/mlbb?id={game_id}&zone={zone_id}"
                    r2 = requests.get(url2, headers=headers, timeout=5).json()
                    user_name = r2.get("username") or r2.get("nickname") or r2.get("name")
                except Exception:
                    pass

            # API 3 (Backup 2)
            if not user_name:
                try:
                    url3 = f"https://order-sg.smile.one/api/v1/check-role"
                    payload = {"game": "mobilelegends", "user_id": game_id, "zone_id": zone_id}
                    r3 = requests.post(url3, data=payload, timeout=5).json()
                    if r3.get("status") == 200 and r3.get("username"):
                        user_name = r3.get("username")
                except Exception:
                    pass

            if user_name:
                bot.reply_to(message, f"✅ Account Found!\n\nName: {user_name}\nID: {game_id} ({zone_id})")
            else:
                bot.reply_to(message, f"❌ Account Not Found!\nID: {game_id} / Server: {zone_id}\n(ID သို့မဟုတ် Server ID မှားယွင်းနိုင်ပါသည်)")
        except Exception:
            bot.reply_to(message, "❌ ID စစ်ဆေးရာတွင် အမှားအယွင်း ရှိနေပါသည်။ ခဏကြာမှ ပြန်စမ်းပါ။")
    else:
        bot.reply_to(message, "❌ ပုံစံ မမှန်ပါ။ ဥပမာ - 123456 (1234) အတိုင်း ပို့ပေးပါ။")

# 4. Connection မပြတ်သွားစေရန် Loop ဖြင့် စောင့်ကြည့်ခြင်း
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=60)
    except Exception as e:
        time.sleep(5)
