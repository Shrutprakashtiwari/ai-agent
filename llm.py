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
def decide(query):
    prompt = f"""
You are an AI agent controller.

Respond ONLY in valid JSON.
No explanation. No extra text.

Choose one:

1. calculator
2. rag_tool
3. final

Format EXACTLY:

{{"type": "tool", "tool": "calculator", "input": "..."}}
{{"type": "tool", "tool": "rag_tool" , "input": "..."}}
{{"type": "final", "output": "..."}}
User: {query}

ONLY JSON:

"""
    response = call_llm(prompt)

    start = response.find("{")
    end = response.rfind("}") + 1

    json_str = response[start:end]

    return json.loads(json_str)

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
        input_query=input()
        if input_query.lower() == "exit":
            break
        decision = decide(input_query)
        if decision["type"]=="tool":
            if decision["tool"]=="calculator":
                result=calculate(decision["input"])
                print("Calculator Result:", result)
            elif decision["tool"]=="rag_tool":
                result=rag_tool(decision["input"])
                print("RAG Result:", result)
            print("Decision:", decision)
        else:
            print("Final Result:", decision["output"])

if __name__=="__main__":
    run()