from flask import Flask, render_template, request
from openai import OpenAI

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)


#Memory storage
chat_history = []

#Limiting memory size
def trim_history():
    while len(chat_history) > 6:
        chat_history.pop(0)

#classifying different tasks
def classify_task(text):
    text = text.lower()

    if "email" in text or "write" in text:
        return "email"
    elif "expense" in text or "spend" in text or "summary" in text or "summarize" in text:
        return "finance"
    elif "suggest" in text or "improve" in text:
        return "insight"
    else:
        return "general"
    

#Different agents
def email_agent(text):
    messages = [
        {"role": "system", "content": "You are a professional finance assistant who writes clear and formal emails."}
    ] + chat_history + [
        {"role": "user", "content": text}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    return response.choices[0].message.content

def finance_agent(text):
    messages = [
        {"role": "system", "content": "You are a financial analyst who summarizes and analyzes expenses clearly."}
    ] + chat_history + [
        {"role": "user", "content": text}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    return response.choices[0].message.content

def insight_agent(text):
    messages = [
        {"role": "system", "content": "You provide helpful financial improvement suggestions."}
    ] + chat_history + [
        {"role": "user", "content": text}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    return response.choices[0].message.content

def general_agent(text):
    messages = chat_history + [
        {"role": "user", "content": text}
    ]
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    return response.choices[0].message.content


#Agent routers
def route_task(task,text):
    if task == "email":
        return email_agent(text)
    elif task == "finance":
        return finance_agent(text)
    elif task == "insight":
        return insight_agent(text)
    else:
        return general_agent(text)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    user_input = request.form['query']

    chat_history.append({"role":"user","content":user_input})
    trim_history()


    task = classify_task(user_input)
    result = route_task(task,user_input)


    chat_history.append({"role":"assistant","content":result})
    trim_history()


    explanation = f"""
    Task: {task}
    Agent Used: {task}_agent
    Reason: Based on keywords and intent in user query
    """

    return render_template('index.html',result=result,task=task,explanation=explanation,history=chat_history)

if __name__== '__main__':
    app.run(debug=True)