# ⚡ Universal AI Resume Architect & ATS Tailor

> **Multi-Agent Resume Optimization System** powered by **LangChain**, **Ollama (Local LLMs: Qwen 2.5 & Gemma 3)**, **PyPDF**, and **ReportLab**. Analyzes **ANY candidate resume** against **ANY job description (JD)** to optimize ATS match scores and export standard-setting, ATS-compliant PDF resumes.

![AI Resume Architect Architecture](./docs/architecture.png)

---

## 🌟 Overview

The **Universal AI Resume Architect & ATS Tailor** is a privacy-first, 100% local multi-agent system designed to optimize tech resumes for any software engineering role, company, or job description. By combining **PyPDF** text extraction with **LangChain** agent orchestration and **Ollama local LLMs**, the application conducts a deep ATS (Applicant Tracking System) audit and rewrites resume bullet points using the **STAR Method** (Situation, Task, Action, Result).

### 🎯 Key Highlights:
- **Universal Compatibility:** Works with any PDF resume input and any target Job Description (SDE Intern, Full-Time SDE, Backend, Frontend, AI/ML, DevOps, etc.).
- **Zero Cloud API Dependencies:** Runs 100% locally via Ollama (`qwen2.5:latest` and `gemma3:4b`), keeping user resumes 100% private.
- **Dual AI Agent Pipeline:** 
  - **Agent 1 (ATS & Skill Gap Auditor):** Computes ATS score, identifies missing keywords, flags weak bullet points, and checks company cultural alignment.
  - **Agent 2 (STAR Resume Architect):** Rewrites experiences and project descriptions into high-impact STAR bullet points with quantifiable metrics.
- **Automated PyPDF Text Extraction:** Parses PDF resumes into structured text sections seamlessly.
- **ATS-Compliant PDF Generation:** Compiles optimized content into a clean single-page PDF using ReportLab.
- **Interactive Streamlit Web Dashboard:** Modern dark-mode UI with live ATS gauges, side-by-side comparisons, preset JDs, and instant PDF download.

---

## 🏗️ Architecture & Workflow

```mermaid
graph TD
    A[📄 Upload Any Resume PDF] -->|PyPDF Parser| B[Raw Text & Sections]
    C[📋 Paste Any Job Description JD] --> D[Agent 1: ATS & Skill Gap Auditor]
    B --> D
    D -->|ATS Score & Gap Analysis| E[Agent 2: STAR Resume Architect]
    B --> E
    C --> E
    E -->|Structured JSON| F[ReportLab PDF Engine]
    F -->|ATS Compliant PDF| G[⬇️ Downloadable Tailored PDF Resume]
    D --> H[Streamlit Interactive Dashboard]
    E --> H
```

---

## 🤖 The 2 AI Agents

### 📊 Agent 1: `ATS & Skill Gap Auditor` (`ats_analyzer_agent.py`)
* **Role:** Evaluates candidate resume text against any target Job Description.
* **LangChain Engine:** Uses `JsonOutputParser` + Pydantic schema validation over `ChatOllama`.
* **Output Metrics:**
  * **ATS Match Score (%)**: Overall compatibility percentage.
  * **Matched Skills**: Overlapping hard skills, tools, and frameworks.
  * **Missing Keywords**: Crucial tech stack & concepts missing from the candidate's profile.
  * **Weak Bullets**: Bullet points lacking metrics or STAR structure.
  * **Cultural & Role Alignment**: Checks for key principles emphasized in the target JD.
  * **Actionable Recommendations**: 3-5 high-priority steps to elevate the candidate's application.

### 📝 Agent 2: `STAR Resume Architect` (`resume_tailor_agent.py`)
* **Role:** Rewrites and optimizes candidate experiences and project descriptions for the target JD.
* **LangChain Engine:** Consumes candidate text + Agent 1 gap analysis to produce structured JSON data.
* **Optimization Highlights:**
  * Rewrites generic descriptions into high-impact STAR-format bullet points.
  * Weaves in missing keywords and key technologies naturally.
  * Preserves truthful candidate experience while elevating technical impact metrics.

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Agent Framework** | [LangChain](https://www.langchain.com/) | Agent chaining, prompt templates, and structured Pydantic output parsing |
| **Local LLM Engine** | [Ollama](https://ollama.com/) | Privacy-preserving local LLM inference (`qwen2.5:latest` & `gemma3:4b`) |
| **PDF Extraction** | [PyPDF](https://pypdf.readthedocs.io/) | Extracting text streams from uploaded PDF resumes |
| **PDF Generation** | [ReportLab](https://www.reportlab.com/) | Rendering ATS-scannable single-page PDF resumes |
| **Web Dashboard** | [Streamlit](https://streamlit.io/) | Interactive web UI with real-time progress indicators |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
Ensure you have Python 3.9+ installed and Ollama running locally:

```bash
# Verify Ollama installation & pull recommended models
ollama pull qwen2.5:latest
ollama pull gemma3:4b
```

### 2. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/ai-resume-architect.git
cd ai-resume-architect

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Streamlit Application

```bash
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501`.

---

## 📁 Repository Structure

```
.
├── app.py                     # Streamlit Web Dashboard
├── ats_analyzer_agent.py      # Agent 1: ATS Auditor (LangChain + Ollama)
├── resume_tailor_agent.py     # Agent 2: Resume Architect (LangChain + Ollama)
├── pdf_parser.py              # PyPDF text extraction module
├── pdf_generator.py           # ReportLab ATS PDF generation engine
├── docs/                      # Documentation & Architecture diagrams
│   └── architecture.png       # High-resolution architecture flow diagram
├── requirements.txt           # Project Python dependencies
└── README.md                  # Project documentation
```

---

## 📜 License

MIT License © 2026 Karthik Vangapandu
