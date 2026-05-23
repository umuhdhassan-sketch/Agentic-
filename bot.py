import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # A nan ne za ka sanya logic din GROQ 
    # Amma don mu fara, bari kawai mu nuna cewa yana aiki
    print("Sakon ya shigo!") 
    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    return "Bot yana aiki!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
