from flask import Flask, render_template, request, jsonify
import json
from openai import OpenAI
from config import OPENAI_API

app = Flask(__name__)

client = OpenAI(api_key=OPENAI_API)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    
    # read chat file and update with most recent user message
    with open('current_chat.json', 'r') as f:
        messages = json.load(f)
    print(messages)
    if len(messages) == 0:
        messages.append({"role": "system", "content": "You are a helpful assistant."})
    user_message = request.form['message']
    messages.append({"role": "user", "content": user_message})
    
    # get response and save to chat file
    completion = client.chat.completions.create(model="gpt-4o-mini",  messages = messages)
    bot_message = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": bot_message})
    with open('current_chat.json', 'w') as f:
        json.dump(messages, f)
        
    return jsonify({'response': bot_message})

if __name__ == '__main__':
    app.run(debug=True)
