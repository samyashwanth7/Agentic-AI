from dotenv import load_dotenv
import os
import ast
import operator as op
import streamlit as st
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()

# ----------------------------
# Setup
# ----------------------------
model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

search = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

# ----------------------------
# Tools
# ----------------------------
def calculator_tool(expression):
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            return operators[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](_eval(node.operand))
        raise TypeError("Unsupported expression")

    try:
        result = _eval(ast.parse(expression, mode="eval").body)
        return {"tool": "calculator", "input": expression, "result": str(result)}
    except Exception:
        return {"tool": "calculator", "input": expression, "result": "Invalid expression"}

def web_search_tool(query):
    try:
        result = search.invoke(query)
        return {"tool": "web_search", "input": query, "result": str(result)}
    except Exception as e:
        return {"tool": "web_search", "input": query, "result": f"Search error: {str(e)}"}

# ----------------------------
# ReAct-style loop
# ----------------------------
def mini_react(question):
    tool_selector_prompt = f"""
You are a tool-choosing assistant.

Available tools:
1. calculator -> use for math expressions
2. web_search -> use for current events, recent facts, live information

User question:
{question}

Rules:
- If the question needs math, respond with:
TOOL: calculator
INPUT: <math expression only>

- If the question needs current/live/recent factual info, respond with:
TOOL: web_search
INPUT: <search query>

- If no tool is needed, respond with:
TOOL: none
INPUT: none

Only return exactly in this format:
TOOL: ...
INPUT: ...
"""

    tool_decision = model.invoke(tool_selector_prompt).content.strip()

    tool_name = "none"
    tool_input = "none"

    for line in tool_decision.splitlines():
        if line.startswith("TOOL:"):
            tool_name = line.replace("TOOL:", "").strip()
        elif line.startswith("INPUT:"):
            tool_input = line.replace("INPUT:", "").strip()

    if tool_name == "calculator":
        tool_output = calculator_tool(tool_input)
    elif tool_name == "web_search":
        tool_output = web_search_tool(tool_input)
    else:
        final_prompt = f"""
User question:
{question}

Answer directly and clearly.
"""
        final_answer = model.invoke(final_prompt).content
        return {
            "thought": "No tool needed",
            "action": "none",
            "observation": "Answered directly",
            "answer": final_answer
        }

    final_prompt = f"""
You are a helpful assistant.

User question:
{question}

Tool used:
{tool_output['tool']}

Tool input:
{tool_output['input']}

Observation / tool result:
{tool_output['result']}

Using this observation, answer the user clearly and briefly.
"""

    final_answer = model.invoke(final_prompt).content

    return {
        "thought": f"Need to use {tool_name}",
        "action": f"{tool_name}({tool_input})",
        "observation": tool_output["result"],
        "answer": final_answer
    }

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Mini ReAct Agent", page_icon="🤖")
st.title("🤖 Mini ReAct Agent")
st.caption("Groq + Tavily + ReAct-style loop")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and "debug" in msg:
            with st.expander("See ReAct steps"):
                st.write(f"**Thought:** {msg['debug']['thought']}")
                st.write(f"**Action:** {msg['debug']['action']}")
                st.write(f"**Observation:** {msg['debug']['observation']}")

if question := st.chat_input("Ask a math or current-facts question..."):
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = mini_react(question)
            st.write(result["answer"])

            with st.expander("See ReAct steps"):
                st.write(f"**Thought:** {result['thought']}")
                st.write(f"**Action:** {result['action']}")
                st.write(f"**Observation:** {result['observation']}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "debug": result
    })