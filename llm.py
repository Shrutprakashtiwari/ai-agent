from multiprocessing import context
import re
# from urllib import response

import requests
import json
def call_llm(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]
def decide(context):
    prompt = f"""
You are an AI agent.

You can:
1. use calculator
2. use rag_tool
3. give final answer
IMPORTANT RULES:
- If a Tool result is already present, DO NOT use the same tool again
- Use the Tool result to produce the final answer
- Repeating the same tool is incorrect

Respond ONLY in JSON.

Context:
{context}

Format:
{{"type": "tool", "tool": "calculator", "input": "..."}}
{{"type": "tool", "tool": "rag_tool", "input": "..."}}
{{"type": "final", "output": "..."}}
"""

    response = call_llm(prompt)

    try:
        match = re.search(r'\{.*?\}', response, re.DOTALL)

        if match:
            return json.loads(match.group())
        else:
            return {"type": "final", "output": response}

    except:
        return {"type": "final", "output": response}

def calculate(expression):
    try:
        return eval(expression)
    except:
        return "Error"
def rag_tool(query):
    knowledge = {
        "rag": "RAG means Retrieval Augmented Generation.",
        "llm": "LLM stands for Large Language Model."
    }

    for key in knowledge:
        if key in query.lower():
            return knowledge[key]

    return "No info found"
def run():
    while True:
        user_input=input()
        if user_input.lower() == "exit":
            break
        context = f"user: {user_input}"
        while True:
            decision = decide(context)
            if decision["type"]=="tool":
                if decision["tool"]=="calculator":
                    result=calculate(decision["input"])
                    print("Calculator Result:", result)
                elif decision["tool"]=="rag_tool":
                    result=rag_tool(decision["input"])
                    print("RAG Result:", result)
                print("Decision:", decision)
                context += f"\ntool_result: {result}\nNow decide next step carefully."
            else:
                print("Final Result:", decision["output"])
                break

if __name__=="__main__":
    run()
