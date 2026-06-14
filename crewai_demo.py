from dotenv import load_dotenv
import os
from crewai import Agent, Task, Crew, Process, LLM

# 👇 THE FIX: Monkey-patch the cache flag injection to bypass the bug
import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg
# 👆 END FIX

load_dotenv()

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

# ── AGENTS ───────────────────────────────────────────
researcher = Agent(
    role="Research Analyst",
    goal="Find the most important facts and key points about the given topic",
    backstory="""You are an expert researcher who digs deep into topics 
    and extracts the most relevant, accurate bullet points.""",
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Write a clear, engaging explanation based on research notes",
    backstory="""You are a skilled writer who transforms raw research 
    into student-friendly, well-structured explanations.""",
    llm=llm,
    verbose=True
)

reviewer = Agent(
    role="Quality Reviewer",
    goal="Review the written content and provide a score with honest feedback",
    backstory="""You are a strict but fair reviewer who evaluates 
    content quality, accuracy, and clarity.""",
    llm=llm,
    verbose=True
)

# ── TASKS ────────────────────────────────────────────
topic = "How Multi-Agent AI Systems Work"

research_task = Task(
    description=f"""Research the following topic and gather 6 key bullet points.
    Topic: {topic}
    Keep points factual, short, and clear.""",
    expected_output="A list of 6 clear bullet points about the topic.",
    agent=researcher
)

write_task = Task(
    description=f"""Using the research notes provided, write a clear explanation.
    Topic: {topic}
    Write 3-4 student-friendly paragraphs. No bullet points.""",
    expected_output="A 3-4 paragraph explanation of the topic.",
    agent=writer
)

review_task = Task(
    description=f"""Review the written content about: {topic}
    Provide:
    1. VERDICT: Approved / Needs Improvement
    2. SCORE: X/10
    3. STRENGTHS: 2 things done well
    4. IMPROVEMENTS: 1-2 suggestions
    5. FINAL NOTE: one sentence summary""",
    expected_output="A structured review with verdict, score, strengths, improvements.",
    agent=reviewer
)

# ── CREW ─────────────────────────────────────────────
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, write_task, review_task],
    process=Process.sequential,
    verbose=True
)

# ── RUN ──────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 Starting CrewAI pipeline...\n")
    result = crew.kickoff()

    print("\n" + "="*60)
    print("✅ FINAL OUTPUT")
    print("="*60)
    print(result)