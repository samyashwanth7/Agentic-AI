# Agentic AI Projects

This repository contains a set of beginner-friendly **agentic AI** projects built while learning concepts like basic chat apps, memory, RAG, ReAct, ReWOO, and multi-agent systems. It is written as both a portfolio repository for first-time visitors and a personal memory document so the project can be understood later without having to rediscover everything.

## Repository purpose

This repo is meant to do two jobs:

- Show the progression from simple LLM apps to more advanced agentic AI workflows.
- Act as a personal reference for what each file does, how it was run, what problems happened, and how they were fixed.

Instead of scattering related experiments into many small repositories, the projects are grouped into one place so the learning path is easier to follow.

## Projects included

| File | Purpose | Main idea |
|------|---------|-----------|
| `app.py` | Basic AI app | Simple LLM interaction through Streamlit |
| `app_memory.py` | Memory-based app | Adds memory or conversational context |
| `rag_app.py` | RAG app | Retrieval-Augmented Generation using local/project knowledge |
| `agent.py` | Tool/agent logic | Core agent-related logic |
| `app_react.py` | ReAct agent | Reasoning + action loop using tools |
| `app_rewoo.py` | ReWOO app | Planner/worker style reasoning workflow |
| `multi_agent_app.py` | Multi-agent app | Multiple agents working together |
| `multi_agent_demo.py` | Multi-agent demo | Demo version of multi-agent behavior |
| `crewai_demo.py` | CrewAI example | Experiment using CrewAI framework |
| `main.py` | Entry/support file | General execution or helper logic |
| `knowledge.txt` | Knowledge source | Local text used for retrieval or context |

## What was learned

These projects were used to understand the following ideas:

- How to build Streamlit-based LLM applications.
- How agents use tools such as search or calculators.
- How memory changes chatbot behavior.
- How RAG works with external or local knowledge.
- How ReAct works using a loop of Thought, Action, Observation, and Final Answer.
- How ReWOO differs by separating planning and execution.
- How multiple agents can collaborate on one task.
- How to structure projects for GitHub and avoid pushing unnecessary files.

## Project flow

A simple way to understand the learning progression in this repo is:

1. Start with a basic chat app.
2. Add memory.
3. Add retrieval with RAG.
4. Add tools and agent behavior.
5. Build ReAct-style reasoning.
6. Build ReWOO-style planning.
7. Move to multi-agent systems.

That means the repo is not just a collection of random files. It shows the path from simple LLM usage to more structured agentic AI patterns.

## Tech stack

The exact stack may vary slightly by file, but the main tools used across the repo are:

- Python
- Streamlit
- LLM APIs such as Groq
- LangChain or custom agent loops depending on the file
- Local text knowledge files for RAG experiments
- `.env` for secret API keys

## How to run the apps

First create and activate a virtual environment if needed.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available yet, install the needed libraries manually, for example:

```bash
pip install streamlit groq python-dotenv requests langchain
```

### Run a Streamlit app

Use this pattern:

```bash
python -m streamlit run filename.py
```

Examples:

```bash
python -m streamlit run app.py
python -m streamlit run app_memory.py
python -m streamlit run rag_app.py
python -m streamlit run app_react.py
python -m streamlit run app_rewoo.py
python -m streamlit run multi_agent_app.py
python -m streamlit run multi_agent_demo.py
```

## Important note about Streamlit errors

One common mistake was running Streamlit files using normal Python, such as:

```bash
python multi_agent_demo.py
```

That causes warnings like:

- `missing ScriptRunContext`
- `Session state does not function when running a script without streamlit run`

### Fix

Run Streamlit apps like this instead:

```bash
python -m streamlit run multi_agent_demo.py
```

This applies to any file that uses `streamlit as st`.

## Environment variables

Some files need API keys. These should be stored in a `.env` file and never pushed to GitHub.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

Depending on the project version, other keys may also be required.

## GitHub upload notes

A major part of the setup process was learning what should and should not be pushed.

### Files and folders that should NOT be pushed

These are local/system/generated files and should stay out of the repo:

- `venv/`
- `.venv/`
- `__pycache__/`
- `*.pyc`
- `.env`

### Recommended `.gitignore`

```gitignore
venv/
.venv/
__pycache__/
*.pyc
.env
```

## Problems faced and fixes

This section is written mainly as a memory aid so the same issues do not have to be debugged again.

### 1. Streamlit warnings about `ScriptRunContext`

**Problem:**
A Streamlit file was run like a normal Python script.

**Symptoms:**
- `missing ScriptRunContext`
- session state warnings
- browser app not opening correctly

**Fix:**
Run with:

```bash
python -m streamlit run filename.py
```

### 2. ReAct file confusion

**Problem:**
One of the ReAct files was not saved or got mixed up with another version.

**Fix:**
Re-created `app_react.py` and made sure the correct version matched the intended API and LLM stack.

### 3. Wrong LLM/provider used in code

**Problem:**
A version of the code used IBM WatsonX even though the intended provider for the project was Groq.

**Fix:**
Replace the IBM-specific setup with Groq API usage and store the key in `.env`.

### 4. Groq model decommissioned

**Problem:**
Using an old Groq model name caused an error like model decommissioned.

**Fix:**
Update the code to a currently supported Groq model and avoid relying on outdated model IDs.

### 5. Git trying to add `venv`

**Problem:**
Git started tracking thousands of files from `venv`.

**Symptoms:**
- too many files shown
- line ending warnings
- messy repository state

**Fix:**
Add a `.gitignore` and remove cached tracking:

```bash
git rm -r --cached venv
git rm -r --cached __pycache__
git rm --cached .env
```

### 6. LF / CRLF warnings

**Problem:**
Git on Windows showed warnings like `LF will be replaced by CRLF`.

**Meaning:**
This is usually a line-ending warning, not a fatal error.

**Fix:**
The main practical fix was making sure Git was not trying to track files inside `venv` in the first place.

### 7. `origin` not found

**Problem:**
Git gave errors like:

```bash
fatal: 'origin' does not appear to be a git repository
```

**Fix:**
Add or reset the remote URL:

```bash
git remote add origin https://github.com/USERNAME/REPO.git
```

or

```bash
git remote set-url origin https://github.com/USERNAME/REPO.git
```

### 8. `Repository not found`

**Problem:**
GitHub push failed because the repo URL was wrong, the repository name was incorrect, or the repository did not exist yet.

**Fix checklist:**
- Check that the repo exists on GitHub.
- Copy the exact HTTPS URL from the GitHub repo page.
- Re-add the remote if needed.
- Make sure the correct GitHub account is being used.

## Useful Git commands to remember

These are the only commands really needed for basic work.

### Start repo

```bash
git init
git branch -M main
```

### Check status

```bash
git status
```

### Add files

```bash
git add .
```

### Commit

```bash
git commit -m "your message"
```

### Add remote

```bash
git remote add origin https://github.com/USERNAME/REPO.git
```

### Push

```bash
git push -u origin main
```

### Check remote

```bash
git remote -v
```

### Stop tracking local-only folders

```bash
git rm -r --cached venv
git rm -r --cached __pycache__
git rm --cached .env
```

## Suggested repository structure

```text
Agentic-AI/
├── app.py
├── app_memory.py
├── app_react.py
├── app_rewoo.py
├── rag_app.py
├── multi_agent_app.py
├── multi_agent_demo.py
├── crewai_demo.py
├── agent.py
├── main.py
├── knowledge.txt
├── README.md
├── .gitignore
└── requirements.txt
```

## What to improve later

This repository is a learning repo, so several improvements can still be made:

- Add a proper `requirements.txt`
- Add screenshots of each app
- Add per-file explanations with sample input/output
- Refactor repeated code into reusable helper functions
- Add better error handling for APIs
- Add a cleaner project structure with folders if the repo grows larger

## Personal reminder section

If this repo is revisited later and the details are forgotten, remember this:

- Most files are Streamlit apps, so run them using `python -m streamlit run filename.py`.
- Do not push `venv`, `__pycache__`, or `.env`.
- If GitHub push fails, first check `git remote -v` and confirm the exact repo URL.
- If Groq code fails, check whether the API key is loaded and whether the model name is still valid.
- If a file seems missing, check whether it was actually saved before debugging anything else.

## Final note

This repository represents the process of learning by building. It includes experiments, fixes, mistakes, reworks, and improvements. That is intentional. The goal is not only to store final code, but also to preserve the path taken to understand agentic AI systems.
