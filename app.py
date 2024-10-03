from flask import Flask, render_template, request, jsonify
import json
import os
from openai import OpenAI
from config import OPENAI_API
from pydantic import BaseModel


class LanguageSkillMemory(BaseModel):
    short_description_of_language_level: str
    summary_of_sessions: list[str]
    vocabulary: list[str]
    grammatical_accuracy_tense_syntax: list[str]
    reading_comprehension: list[str]
    writing_expression_and_clarity: list[str]
    conversation_interaction_skills: list[str]

app = Flask(__name__)

client = OpenAI(api_key=OPENAI_API)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # read in memory
    with open('language_skill_memory.json', 'r') as f:
        mem = json.dumps(json.load(f), indent=4)
    # read chat file and update with most recent user message
    if not os.path.exists('current_chat.json'):
        with open('current_chat.json', 'w') as f:
            json.dump([], f)
    with open('current_chat.json', 'r') as f:
        messages = json.load(f)
    print(messages)
    if len(messages) == 0:
        messages.append({"role": "system", "content": f"You are a Spanish teacher for a student.  You are enthusiastic about getting the student to the next language level.  You interact with the student by speaking spanish (unless english is needed), and you evaluate the student using review and exams of grammar, vocabulary, reading, and writing.  Here is what we know about the student's history of learning and level in json format.  {mem}"})
    user_message = request.form['message']
    messages.append({"role": "user", "content": user_message})
    
    # get response and save to chat file
    completion = client.chat.completions.create(model="gpt-4o-mini",  messages = messages)
    bot_message = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": bot_message})
    with open('current_chat.json', 'w') as f:
        json.dump(messages, f)
        
    return jsonify({'response': bot_message})

def update_memory():
    with open('language_skill_memory.json', 'r') as f:
        mem = json.dumps(json.load(f), indent=4)
        
    with open('current_chat.json', 'r') as f:
        currchat = json.dumps(json.load(f), indent=4)
    
    messages = [{"role": "system", "content": "You are a Spanish teacher, and you are evaluating the performance of using a specified json format.  This format stores how well the student is performing across various language dimensions.  You will be given the stored performance, and your task is to update it.  Keep in mind that this performance evaluation is additive in nature.  So your preference is to not delete any information which is already present, unless it is necessary to edit something to reflect the student's new abilities."}]
    
    prompt = f"""
    The student just completed a session with the teacher which is captured in the following message format: the teacher is the 'assistant' and the student is the 'user'.
    
    {currchat}
    
    Please update the following json using the information present in this session.  
        - short_description_of_language_level: Update the 'short_description_of_language_level' if and only if anything the student did during this session was worth updating it.  This should include the approximate level of the student as A1, A2, B1, B2, C1, or C2 (common European framework).  Be strict in what level you assign.  The student must prove mastery in the relevant areas in order to advance to the next level.  By default, you assume the student doesn't know something unless it is proven in an interaction.  The level assignment should also include a short set of what needs to be learned to get to the next level.
        - summary_of_sessions: Append to the list within the 'summary_of_sessions' to include a short summary of what the student accomplished in this session.  Include details such as what topics the student learned and the methods which were used to evaluate the student (e.g. review, grammar test, vocab exam).
        - vocabulary: Append to the list within the 'vocabulary' to include any new vocabulary words the student learned during this session.
        - grammatical_accuracy_tense_syntax: Append to the list within the 'grammatical_accuracy_tense_syntax' to include any new grammatical rules the student learned during this session.  This should include any new tenses or syntax rules.  Also, within each element of the list include a note about how well the student performs (e.g. struggling, improving, mastered).
        - reading_comprehension: Append to the list within the 'reading_comprehension' to include any new reading comprehension exercises the student completed during this session.  Make sure that each element of the list include a note about how well the student performed.
        - writing_expression_and_clarity: Append to the list within the 'writing_expression_and_clarity' to include any new writing exercises the student completed during this session.  Make sure that each element of the list includes a note about how well the student performed. 
        - conversation_interaction_skills: Append to the list within the 'conversation_interaction_skills' to include any new notable skills the student obtained during this session.  Make sure that each element of the list includes a note about how well the student performed.   
        
    {mem}
    """
    
    messages.append({"role": "user", "content": prompt})
    completion = client.beta.chat.completions.parse(model="gpt-4o-mini",  messages = messages, response_format=LanguageSkillMemory)
    mem_updated = completion.choices[0].message.content
    print("memory updated!", mem_updated)
    
    with open('language_skill_memory.json', 'w') as f:
        json.dump(json.loads(mem_updated), f, indent=4)
    return

@app.route('/end_session', methods=['POST'])
def end_session():
    print("entered the End_Session end point in python code!")
    
    print("updating memory")
    update_memory()
    return jsonify({'message': 'Session ended and memory updated successfully!'})
    # except Exception as e:
    #     print('exception occured')
    #     return jsonify({'message': f'Error ending session: {str(e)}'})

    
    

if __name__ == '__main__':
    app.run(debug=True)
