import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# Define Pydantic Schema for Agent 2 Tailored Resume Output
class ProjectItem(BaseModel):
    name: str = Field(description="Project name")
    tech_stack: str = Field(description="Comma-separated tools and technologies used")
    bullet_points: List[str] = Field(description="High-impact STAR bullet points with action verbs and quantifiable results")

class ExperienceItem(BaseModel):
    title: str = Field(description="Job title or role name")
    organization: str = Field(description="Company or Organization name")
    duration: str = Field(description="Duration e.g. Jun 2024 - Present")
    location: str = Field(description="Location e.g. Bengaluru, India")
    bullet_points: List[str] = Field(description="High-impact STAR bullet points highlighting engineering craft, metrics, and technical contributions")

class TailoredResume(BaseModel):
    full_name: str = Field(description="Candidate's full name")
    headline: str = Field(description="Professional title e.g., Software Development Engineer Intern")
    contact: Dict[str, str] = Field(description="Dict with keys: email, phone, github, linkedin, location")
    summary: str = Field(description="2-3 sentence compelling summary emphasizing code craft, problem solving, and HackerRank alignment")
    skills: Dict[str, List[str]] = Field(description="Categorized skills dictionary e.g. {'Languages': [...], 'Frameworks & Tools': [...], 'Core CS': [...]}")
    experience: List[ExperienceItem] = Field(description="Tailored experience entries")
    projects: List[ProjectItem] = Field(description="Tailored project entries")
    education: List[Dict[str, str]] = Field(description="Education entries e.g. [{'degree': '...', 'institution': '...', 'year': '...'}]")

def tailor_resume(resume_text: str, jd_text: str, ats_gap_analysis: dict, model_name: str = "qwen2.5:latest") -> dict:
    """
    Agent 2: Tailors and optimizes resume content based on JD and Agent 1's gap analysis.
    Uses LangChain and Ollama (qwen2.5:latest).
    """
    llm = ChatOllama(
        model=model_name,
        temperature=0.3,
    )

    parser = JsonOutputParser(pydantic_object=TailoredResume)

    system_prompt = (
        "You are an elite AI Resume Architect and Senior Engineering Mentor.\n"
        "Your goal is to rewrite and optimize a candidate's resume content to make it standard-setting for a target Job Description.\n"
        "Follow these rules:\n"
        "1. Transform generic descriptions into strong STAR-format bullet points (Situation, Task, Action, Result).\n"
        "2. Seamlessly integrate key missing skills from the ATS audit where applicable.\n"
        "3. Reflect engineering craft, developer tool passion, clean code, and human+AI side-by-side efficiency (key HackerRank values).\n"
        "4. Keep information truthful to candidate experience, but elevate the technical phrasing and impact metrics.\n\n"
        "Return ONLY a valid JSON object matching the requested schema.\n"
        "{format_instructions}"
    )

    human_prompt = (
        "TARGET JOB DESCRIPTION:\n"
        "----------------------\n"
        "{jd_text}\n\n"
        "ORIGINAL RESUME TEXT:\n"
        "--------------------\n"
        "{resume_text}\n\n"
        "AGENT 1 ATS GAP AUDIT:\n"
        "----------------------\n"
        "{gap_analysis_json}\n\n"
        "Generate the optimized, tailored resume JSON structure now."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    chain = prompt | llm | parser

    gap_analysis_str = json.dumps(ats_gap_analysis, indent=2)

    try:
        result = chain.invoke({
            "jd_text": jd_text,
            "resume_text": resume_text,
            "gap_analysis_json": gap_analysis_str,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    except Exception as e:
        print(f"Warning: JSON output parsing error ({e}), retrying raw cleanup...")
        raw_chain = prompt | llm
        raw_res = raw_chain.invoke({
            "jd_text": jd_text,
            "resume_text": resume_text,
            "gap_analysis_json": gap_analysis_str,
            "format_instructions": parser.get_format_instructions()
        })
        content = raw_res.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        return json.loads(content.strip())

if __name__ == "__main__":
    sample_jd = """
    HackerRank Software Development Engineer Intern
    Looking for interns who care deeply about code craft, developer tools, and human+AI side-by-side development.
    Requires strong Python/C++/Java skills, data structures, algorithms, REST APIs, Git, and automated testing.
    6-month full-time onsite internship in Bengaluru.
    """

    sample_resume = """
    Karthik Vangapandu
    Email: karthik@example.com | Phone: +91 9876543210 | GitHub: github.com/karthik
    Software Engineer Student
    Skills: Python, JavaScript, HTML/CSS, Git, SQL, React.
    Experience: Built a web project with React and Node.js. Wrote Python scripts for data processing.
    Education: B.Tech in Computer Science (2023 - 2027), ABC Institute of Technology.
    """

    sample_gap_analysis = {
        "ats_score": 65,
        "matched_skills": ["Python", "Git"],
        "missing_keywords": ["C++", "Java", "Data Structures", "Algorithms", "REST APIs", "Automated Testing"],
        "weak_bullets": ["Built a web project with React and Node.js.", "Wrote Python scripts for data processing."]
    }

    print("Testing Agent 2 (Resume Architect & Tailor) with Ollama qwen2.5:latest...")
    tailored = tailor_resume(sample_resume, sample_jd, sample_gap_analysis)
    print("\n--- Agent 2 Output ---")
    print(json.dumps(tailored, indent=2))
