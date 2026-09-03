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
use this when you have enough information to answer the user's question.Only give a final answer without tools if the answer is obvious and does not require external information or calculation.3
IMPORTANT RULES:
- If a Tool result is already present, DO NOT use the same tool again
- Use the Tool result to produce the final answer
- Repeating the same tool is incorrect
If a tool has already returned a result, you MUST use that result.
Do NOT override or change tool outputs.
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
        match = re.search(r'\[.*?\]', response, re.DOTALL)

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

Split the user query into all required sub-tasks.

Each sub-task MUST be solved using the correct tool.

If the query contains multiple parts, you MUST include a step for each part.

Do NOT skip any required tool.

Do NOT go to the final step until ALL required tool steps are completed.
Use ONLY the tools that are necessary to answer the query.

- If a part of the query requires calculation, use calculator.
- If a part requires factual knowledge, use rag_tool.
- If a part can be answered directly, do NOT use any tool for that part.

Do NOT use unnecessary tools.
Each step must be one of:
- calculator
- rag_tool
- final

Do not include any explanation, text, or formatting outside the JSON list.
You MUST ALWAYS include a final step as the last step.

The final step MUST be:
{{"step": N, "tool": "final", "input": "use previous results to answer"}}
The "input" field of the final step must describe how to combine previous results. It must NOT be "...".

Even if there is only one tool step, you MUST still include the final step.

The output is INVALID if the final step is missing.
Return ONLY JSON list.

Format:
[{
  {"step": 1, "tool": "calculator", "input": "23+23"},
  {"step": 2, "tool": "rag_tool", "input": "llm"},
  {"step": 3, "tool": "final", "input": "combine calculator and rag_tool outputs into a final answer"}
}]

User:
{query}
"""
    response = call_llm(prompt)
    try:
        parsed = json.loads(response)
        if isinstance(parsed, dict):
            parsed = [parsed]
        return parsed
    except:
        pass
    
    match = re.search(r'\[.*?\]', response, re.DOTALL)
    
    if match:
                return json.loads(match.group())
                # if isinstance(parsed, dict):
                #     print([parsed])
    else:
                return {"type": "final", "output": response}
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, dict):
                parsed = [parsed]
            return parsed
        except:
            pass
    return [
    {"tool": "final", "input": "answer directly without tools"}
]

def run():
    while True:
        user_input=input()
        if user_input.lower() == "exit":
            break

        steps=plan(user_input)
        plan_success=False
        last_result=None
        resultss=[]
        print("DEBUG steps:", steps)
        print("Type:", type(steps))
        for step in steps:

            tool = step["tool"]
            input_val = step["input"]
            if tool=="calculator":
                result=calculate(input_val)
                last_result=result
                resultss.append({
                    "type": "tool",
                    "tool": "calculator",
                    "input": input_val,
                    "output": result
                })
                print("Calculator Result:", result)
            elif tool=="rag_tool":
                result=rag_tool(input_val)
                last_result=result
                resultss.append({
                    "type": "tool",
                    "tool": "rag_tool",
                    "input": input_val,
                    "output": result
                })
                print("RAG Result:", result)
            elif tool=="final":
                tool_info = ""
                for i, res in enumerate(resultss):
                    if i == 0:
                        tool_info += f"calculator result: {res}\n"
                    elif i == 1:
                        tool_info += f"rag_tool result: {res}\n"
                    else:
                        tool_info += f"result {i}: {res}\n"

                final_prompt = f"""You are a reasoning agent.

                    User query: {user_input}

                    Tool results (JSON):
                    {resultss}

                    Instructions:
                    - Use the tool results to answer the question
                    - Think step-by-step before answering
                    - If results conflict, resolve them logically
                    - If information is missing, say so
                    - Do NOT blindly combine — reason about them
                    - Verify tool outputs before using them
                    - If a tool result seems wrong, question it

                    Final answer:"""

                final_answer = call_llm(final_prompt)
                print("Final Result:", final_answer)

                plan_success = True
                break
                
            else:
                print("Unknown tool:", tool)
                plan_success=False
                break
        if not plan_success:
            if last_result is not None:
                context = f"user: {user_input}\nprevious result: {last_result}"
            else:
                context = f"user: {user_input}"
            last_tool=None
            step_counter=0
            finished=False
            # last_result=None
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
