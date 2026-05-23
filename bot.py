import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)
TOKEN = "8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c"

@app.route('/', methods=['POST'])
def webhook():
    update = request.get_json()
    # A nan ne za ka saka logic dinka na AI (Groq)
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
