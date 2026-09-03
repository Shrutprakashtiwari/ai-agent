import re
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
use this for math calculations only.
eg. 2+2=4
2. use rag_tool
use this for information retrieval from a knowledge base.
3. give final answer
use this when you have enough information to answer the user's question. or you can answer without using any tools.
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
    if not re.fullmatch(r'^[\d\s\+\-\*\/\(\)\.]+$', expression):
        return "Invalid expression"
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
def plan(query):
    prompt = f"""
You are a planning agent.

Break the user request into steps.

Each step must be one of:
- calculator
- rag_tool
- final

Return ONLY JSON list.

Format:
[
  {{"step": 1, "tool": "calculator", "input": "..."}},
  {{"step": 2, "tool": "final", "input": "..."}}
]

User:
{query}
"""
    response = call_llm(prompt)

    start = response.find("[")
    end = response.rfind("]") + 1

    json_str = response[start:end]

    return json.loads(json_str)
def run():
    while True:
        user_input=input()
        if user_input.lower() == "exit":
            break
        context = f"user: {user_input}"
        last_tool=None
        step_counter=0
        finished=False
        last_result=None
        while step_counter<5:
            decision = decide(context)
            step_counter += 1
            # finished=True

            if decision["type"]=="tool" and decision["tool"]==last_tool:
                print("⚠️ Repeated tool detected. Stopping.")
                print("Final Result:", last_result)
                break
            if decision["type"]=="tool":
                if decision["tool"]=="calculator":
                    result=calculate(decision["input"])
                    print("Calculator Result:", result)
                elif decision["tool"]=="rag_tool":
                    result=rag_tool(decision["input"])
                    print("RAG Result:", result)
                last_result = result
                print("Decision:", decision)
                last_tool = decision["tool"]
                context += f"\nStep {step_counter}: Used {decision['tool']} → got {result}"
                context += "\nNext step: think carefully"
                
                
            else:
                output = decision.get("output") or decision.get("input") or decision.get("answer")

                print("Final Result:", output)
                finished=True
                break
        if not finished:
            print("⚠️ Maximum steps reached. Stopping.")
            if last_result is not None:
                print("Final Result:", last_result)
                
            else:
                print("No tools were used. Stopping.")

if __name__=="__main__":
    run()
