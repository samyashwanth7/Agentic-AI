import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import re
import requests

load_dotenv()

# ---------- Groq Setup ----------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"

# ---------- Tools ----------
def search_web(query: str) -> str:
    """Simple search/info tool"""
    results = {
        "AI trends 2025": "Top AI trends: multimodal models, agentic AI, edge AI deployment.",
        "python": "Python is a high-level programming language widely used in AI, ML, automation, and backend development.",
        "weather": "Use a city name to fetch live weather information.",
    }

    q = query.lower()
    for key in results:
        if key.lower() in q:
            return results[key]

    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", f"No specific info found for '{query}'.")
    except Exception:
        pass

    return f"Search result for '{query}': No specific data found."

def calculator(expression: str) -> str:
    """Simple calculator tool"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"

TOOLS = {
    "search_web": search_web,
    "calculator": calculator
}

TOOLS_DESCRIPTION = """
You have access to these tools:
1. search_web(query) - Search the web for information
2. calculator(expression) - Perform mathematical calculations

To use a tool, respond in this EXACT format:
THOUGHT: <your reasoning>
ACTION: <tool_name>
INPUT: <tool input>

When you have the final answer, respond:
THOUGHT: <reasoning>
FINAL ANSWER: <your answer>
"""

# ---------- Groq call ----------
def ask_groq(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful ReAct AI assistant. Follow the exact format given."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ---------- ReAct Loop ----------
def react_agent(user_query: str, max_iterations: int = 5):
    steps = []
    history = f"{TOOLS_DESCRIPTION}\n\nUser Question: {user_query}\n"

    for i in range(max_iterations):
        prompt = history + "\nRespond strictly in the required format."
        response = ask_groq(prompt)
        steps.append({"iteration": i + 1, "llm_output": response})

        if "FINAL ANSWER:" in response:
            final = response.split("FINAL ANSWER:")[-1].strip()
            steps.append({"final_answer": final})
            return steps, final

        action_match = re.search(r"ACTION:\s*(\w+)", response)
        input_match = re.search(r"INPUT:\s*(.+)", response)

        if action_match and input_match:
            tool_name = action_match.group(1).strip()
            tool_input = input_match.group(1).strip()

            if tool_name in TOOLS:
                observation = TOOLS[tool_name](tool_input)
                steps.append({
                    "tool_used": tool_name,
                    "tool_input": tool_input,
                    "observation": observation
                })
                history += f"\n{response}\nOBSERVATION: {observation}\n"
            else:
                history += f"\n{response}\nOBSERVATION: Tool '{tool_name}' not found.\n"
        else:
            steps.append({"final_answer": response.strip()})
            return steps, response.strip()

    return steps, "Max iterations reached. Could not resolve query."

# ---------- Streamlit UI ----------
st.set_page_config(page_title="ReAct Agent", page_icon="🤖", layout="wide")
st.title("🤖 ReAct Agent — Reasoning + Acting")
st.caption("Uses Groq API + ReAct loop: Think → Act → Observe → Repeat")

st.markdown("""
### How ReAct Works
| Step | What Happens |
|------|-------------|
| 🧠 THOUGHT | LLM reasons about what to do next |
| ⚡ ACTION | Calls a tool (search, calculator) |
| 👁️ OBSERVATION | Gets result back from tool |
| 🔁 LOOP | Repeats until final answer found |
""")

user_input = st.text_input("Ask something:", placeholder="e.g. What are the top AI trends in 2025?")
max_iter = st.slider("Max iterations", 1, 10, 5)

if st.button("▶ Run ReAct Agent") and user_input:
    with st.spinner("Agent is thinking and acting..."):
        steps, final_answer = react_agent(user_input, max_iter)

    st.success(f"✅ Final Answer: {final_answer}")

    st.markdown("---")
    st.subheader("🔍 Step-by-Step Trace")

    for step in steps:
        if "llm_output" in step:
            with st.expander(f"🧠 Iteration {step['iteration']} — LLM Output"):
                st.code(step["llm_output"], language="text")
        if "tool_used" in step:
            with st.expander(f"⚡ Tool Used: {step['tool_used']}"):
                st.write(f"**Input:** {step['tool_input']}")
                st.write(f"**Observation:** {step['observation']}")
        if "final_answer" in step:
            st.info(f"🎯 Final Answer: {step['final_answer']}")