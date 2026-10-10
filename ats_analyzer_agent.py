import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# Define Pydantic Schema for Agent 1 Structured Output
class ATSAnalysisResult(BaseModel):
    ats_score: int = Field(description="ATS match percentage from 0 to 100 based on JD requirements")
    matched_skills: List[str] = Field(description="List of skills and keywords present in both resume and JD")
    missing_keywords: List[str] = Field(description="Crucial skills, tools, or keywords present in JD but missing in resume")
    weak_bullets: List[str] = Field(description="Bullet points from resume that lack quantifiable metrics, STAR structure, or strong impact")
    hackerrank_alignment: List[str] = Field(description="Observations on how well the resume reflects values like code craft, AI tools, developer focus, and onsite commitment")
    key_recommendations: List[str] = Field(description="3-5 actionable recommendations to optimize the resume for this specific JD")

def analyze_resume_ats(resume_text: str, jd_text: str, model_name: str = "qwen2.5:latest") -> dict:
    """
    Agent 1: Compares resume text against Job Description using LangChain and Ollama.
    Returns a structured ATS analysis result.
    """
    llm = ChatOllama(
        model=model_name,
        temperature=0.2,
    )

    parser = JsonOutputParser(pydantic_object=ATSAnalysisResult)

    system_prompt = (
        "You are an expert technical recruiter and ATS (Applicant Tracking System) auditing AI agent.\n"
        "Your task is to analyze a candidate's resume text against a specific Job Description (JD).\n"
        "Be thorough, precise, and objective.\n\n"
        "Return your response ONLY as a valid JSON object matching the requested schema.\n"
        "{format_instructions}"
    )

    human_prompt = (
        "JOB DESCRIPTION:\n"
        "----------------\n"
        "{jd_text}\n\n"
        "CANDIDATE RESUME TEXT:\n"
        "---------------------\n"
        "{resume_text}\n\n"
        "Perform the full ATS audit now."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "jd_text": jd_text,
            "resume_text": resume_text,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    except Exception as e:
        # Fallback handling if JSON parsing requires raw extraction
        print(f"Warning: JSON output parsing error ({e}), retrying fallback...")
        raw_chain = prompt | llm
        raw_res = raw_chain.invoke({
            "jd_text": jd_text,
            "resume_text": resume_text,
            "format_instructions": parser.get_format_instructions()
        })
        # Clean potential markdown formatting ```json ... ```
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
    Software Engineer Student
    Skills: Python, JavaScript, HTML/CSS, Git, SQL, React.
    Experience: Built a web project with React and Node.js. Wrote Python scripts for data processing.
    Education: B.Tech in Computer Science.
    """

    print("Testing Agent 1 (ATS & Skill Gap Analyzer) with Ollama qwen2.5:latest...")
    analysis = analyze_resume_ats(sample_resume, sample_jd)
    print("\n--- Agent 1 Output ---")
    print(json.dumps(analysis, indent=2))
