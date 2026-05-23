import os
from flask import Flask, request
from groq import Groq

app = Flask(__name__)
client = Groq(api_key="Gsk_P4Gp6Vcfjcc9NcGXYDSDWGdyb3FYXi5lbYB3W65Xo4MREQD2bOue")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        # Nan ne AI ɗin zai amsa
        if text:
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": text}],
                model="llama3-8b-8192"
            )
            reply = completion.choices[0].message.content
            
            # Amsa zuwa Telegram
            import requests
            requests.post(f"https://api.telegram.org/bot8990797862:AAHey5yxI-YWJtMjOvimfJc7GFSsRTkC57c/sendMessage", 
                          json={"chat_id": chat_id, "text": reply})
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
