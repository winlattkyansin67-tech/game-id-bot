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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # API Method 1: SmileOne Direct Official API
    try:
        url1 = "https://order-sg.smile.one/api/v1/check-role"
        data1 = {"game": "mobilelegends", "user_id": game_id, "zone_id": zone_id}
        res1 = requests.post(url1, data=data1, headers=headers, timeout=6).json()
        if res1.get("status") == 200 and res1.get("username"):
            return res1.get("username")
    except Exception:
        pass

    # API Method 2: Vyturex Server
    try:
        url2 = f"https://api.vyturex.com/mlbb?id={game_id}&zone={zone_id}"
        res2 = requests.get(url2, headers=headers, timeout=6).json()
        if res2.get("name"):
            return res2.get("name")
    except Exception:
        pass

    # API Method 3: Eliasn Backup API
    try:
        url3 = f"https://api.eliasn.my.id/mlbb?id={game_id}&zone={zone_id}"
        res3 = requests.get(url3, headers=headers, timeout=6).json()
        name = res3.get("username") or res3.get("nickname") or res3.get("name")
        if name:
            return name
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
            
            # ID တကယ်ရှိ/မရှိ စစ်ဆေးခြင်း
            user_name = check_mlbb_id(game_id, zone_id)

            if user_name:
                bot.reply_to(message, f"✅ Account Found!\n\nName: {user_name}\nID: {game_id} ({zone_id})")
            else:
                bot.reply_to(message, f"❌ Account Not Found!\nID: {game_id} / Server: {zone_id}\n\n(ID သို့မဟုတ် Server ID မှားယွင်းနေပါသည်)")
        except Exception:
            bot.reply_to(message, "❌ စစ်ဆေးရတာ အဆင်မပြေဖြစ်သွားပါသည်၊ ခဏကြာမှ ပြန်စမ်းပေးပါ။")
    else:
        bot.reply_to(message, "❌ ပုံစံ မမှန်ပါ။ ဥပမာ - 123456 (1234) အတိုင်း ပို့ပေးပါ။")

# 4. Connection မပြတ်သွားစေရန် Loop ဖြင့် စောင့်ကြည့်ခြင်း
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=60)
    except Exception as e:
        time.sleep(5)
