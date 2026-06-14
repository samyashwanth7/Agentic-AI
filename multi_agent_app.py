from dotenv import load_dotenv
import os
import streamlit as st
from langchain_groq import ChatGroq

load_dotenv()

st.set_page_config(page_title="Multi-Agent System", page_icon="🤖", layout="wide")
st.title("🤖 Multi-Agent System")
st.caption("Researcher → Writer → Reviewer working together")

@st.cache_resource
def load_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )

llm = load_llm()

def researcher_agent(topic):
    prompt = f"""You are a Researcher Agent. Your only job is to gather key facts.

Topic: {topic}

Return exactly 6 bullet points:
- factual, short, clear
- no fluff, no intro sentence
- just the bullet points
"""
    return llm.invoke(prompt).content

def writer_agent(topic, research_notes):
    prompt = f"""You are a Writer Agent. Your job is to write a clear explanation.

Topic: {topic}

Research Notes:
{research_notes}

Write a short, well-structured explanation (3-4 paragraphs).
Student-friendly language. No bullet points — flowing paragraphs only.
"""
    return llm.invoke(prompt).content

def reviewer_agent(topic, written_content):
    prompt = f"""You are a Reviewer Agent. Your job is to review the written content below.

Topic: {topic}

Written Content:
{written_content}

Give:
1. VERDICT: (Approved / Needs Improvement)
2. SCORE: X/10
3. STRENGTHS: 2 things done well
4. IMPROVEMENTS: 1-2 specific suggestions (if any)
5. FINAL NOTE: one sentence summary

Be honest and constructive.
"""
    return llm.invoke(prompt).content

# ── UI ──────────────────────────────────────────────────────────
st.divider()

topic = st.text_input("📌 Enter a topic for the agents to work on:", 
                       placeholder="e.g. How RAG works, Benefits of AI in healthcare...")

if st.button("🚀 Run All 3 Agents", type="primary"):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        col1, col2, col3 = st.columns(3)

        # ── AGENT 1: RESEARCHER ──────────────────────────────
        with col1:
            st.markdown("### 🔍 Agent 1: Researcher")
            st.caption("Gathering key facts...")
            with st.spinner("Researching..."):
                research = researcher_agent(topic)
            st.success("✅ Research Done")
            st.markdown(research)

        # ── AGENT 2: WRITER ──────────────────────────────────
        with col2:
            st.markdown("### ✍️ Agent 2: Writer")
            st.caption("Writing explanation from research...")
            with st.spinner("Writing..."):
                article = writer_agent(topic, research)
            st.success("✅ Writing Done")
            st.markdown(article)

        # ── AGENT 3: REVIEWER ────────────────────────────────
        with col3:
            st.markdown("### 🧐 Agent 3: Reviewer")
            st.caption("Reviewing the written content...")
            with st.spinner("Reviewing..."):
                review = reviewer_agent(topic, article)
            st.success("✅ Review Done")
            st.markdown(review)

        # ── SUMMARY BAR ──────────────────────────────────────
        st.divider()
        st.markdown("### 📋 Pipeline Complete")
        st.info(f"**Topic:** {topic}  \n**Flow:** Researcher → Writer → Reviewer  \n**Status:** All 3 agents finished ✅")