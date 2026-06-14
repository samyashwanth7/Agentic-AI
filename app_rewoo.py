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
        return str(result)
    except Exception:
        return "Invalid expression"

def web_search_tool(query):
    try:
        result = search.invoke(query)
        return str(result)
    except Exception as e:
        return f"Search error: {str(e)}"

# ----------------------------
# ReWOO: Planner
# ----------------------------
def create_plan(question):
    planner_prompt = f"""
You are a planner for a ReWOO-style agent.

Available tools:
- calculator: for math expressions
- web_search: for current or factual information

User question:
{question}

Create a short step-by-step plan using ONLY this format:

STEP 1: <tool_name> | <input>
STEP 2: <tool_name> | <input>
...

Rules:
- Use calculator only for pure math.
- Use web_search for current/live/recent factual info.
- If only one step is needed, give one step.
- Final answering will happen later, so do not include the final answer.
- Do not write anything except the STEP lines.
"""
    return model.invoke(planner_prompt).content.strip()

# ----------------------------
# ReWOO: Executor
# ----------------------------
def execute_plan(plan_text):
    executed_steps = []

    for line in plan_text.splitlines():
        line = line.strip()
        if not line.startswith("STEP"):
            continue

        try:
            step_label, rest = line.split(":", 1)
            tool_name, tool_input = rest.split("|", 1)
            tool_name = tool_name.strip()
            tool_input = tool_input.strip()

            if tool_name == "calculator":
                result = calculator_tool(tool_input)
            elif tool_name == "web_search":
                result = web_search_tool(tool_input)
            else:
                result = f"Unknown tool: {tool_name}"

            executed_steps.append({
                "step": step_label.strip(),
                "tool": tool_name,
                "input": tool_input,
                "result": result
            })

        except Exception as e:
            executed_steps.append({
                "step": "STEP ?",
                "tool": "error",
                "input": line,
                "result": f"Execution parsing error: {str(e)}"
            })

    return executed_steps

# ----------------------------
# ReWOO: Final output
# ----------------------------
def rewoo_agent(question):
    plan = create_plan(question)
    executed_steps = execute_plan(plan)

    execution_summary = ""
    for item in executed_steps:
        execution_summary += (
            f"{item['step']}\n"
            f"Tool: {item['tool']}\n"
            f"Input: {item['input']}\n"
            f"Result: {item['result']}\n\n"
        )

    final_prompt = f"""
You are a helpful assistant.

User question:
{question}

Plan:
{plan}

Executed results:
{execution_summary}

Answer the user's question clearly and briefly using the executed results.
"""
    final_answer = model.invoke(final_prompt).content

    return {
        "plan": plan,
        "steps": executed_steps,
        "answer": final_answer
    }

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Tiny ReWOO Agent", page_icon="🧠")
st.title("🧠 Tiny ReWOO Agent")
st.caption("Planner → Executor → Output")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and "debug" in msg:
            with st.expander("See ReWOO steps"):
                st.write("**Plan**")
                st.code(msg["debug"]["plan"])

                st.write("**Executed Steps**")
                for step in msg["debug"]["steps"]:
                    st.write(f"**{step['step']}**")
                    st.write(f"- Tool: {step['tool']}")
                    st.write(f"- Input: {step['input']}")
                    st.write(f"- Result: {step['result']}")

if question := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Planning and executing..."):
            result = rewoo_agent(question)
            st.write(result["answer"])

            with st.expander("See ReWOO steps"):
                st.write("**Plan**")
                st.code(result["plan"])

                st.write("**Executed Steps**")
                for step in result["steps"]:
                    st.write(f"**{step['step']}**")
                    st.write(f"- Tool: {step['tool']}")
                    st.write(f"- Input: {step['input']}")
                    st.write(f"- Result: {step['result']}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "debug": result
    })