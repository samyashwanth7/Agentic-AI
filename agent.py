from dotenv import load_dotenv
import os
import ast
import operator as op
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()

search = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))

model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def safe_eval(expr):
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            return operators[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](_eval(node.operand))
        raise TypeError("Unsupported expression")

    return _eval(ast.parse(expr, mode="eval").body)

def load_knowledge():
    try:
        with open("knowledge.txt", "r", encoding="utf-8") as f:
            text = f.read()
        chunks = [line.strip() for line in text.split("\n") if line.strip()]
        return chunks
    except FileNotFoundError:
        return []

def retrieve(query, chunks, top_k=3):
    query_words = set(query.lower().split())
    scored = []

    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(query_words & chunk_words)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k]]

chat_history = []
knowledge_chunks = load_knowledge()

print("🤖 Multi-Tool RAG Agent Ready!")
print("Tools: 1) Calculator  2) Web Search  3) Knowledge Base")
print("Type 'quit' to exit\n")
print(f"Knowledge base loaded: {len(knowledge_chunks)} chunks\n")

while True:
    question = input("You: ").strip()

    if question.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    chat_history.append(f"User: {question}")

    if any(opr in question for opr in ["+", "-", "*", "/", "**"]):
        try:
            answer = str(safe_eval(question))
        except Exception:
            answer = "Invalid math expression"
    else:
        relevant_chunks = retrieve(question, knowledge_chunks)

        if relevant_chunks:
            print("\nRetrieving from knowledge base...\n")
            context = "\n".join(relevant_chunks)
            tool_used = "Knowledge Base"
        else:
            print("\nSearching web...\n")
            search_result = search.invoke(question)
            context = str(search_result)
            tool_used = "Web Search"

        prompt = f"""
You are a helpful assistant.

Tool used: {tool_used}
Content:
{context}

User question:
{question}

Answer clearly and briefly.
"""
        response = model.invoke(prompt)
        answer = response.content

    chat_history.append(f"Assistant: {answer}")
    print(f"Answer: {answer}\n")