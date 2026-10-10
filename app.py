import streamlit as st
import json
import os
import io

from pdf_parser import extract_text_from_pdf
from ats_analyzer_agent import analyze_resume_ats
from resume_tailor_agent import tailor_resume
from pdf_generator import generate_resume_pdf

# Page Config
st.set_page_config(
    page_title="AI Resume Architect & ATS Tailor for HackerRank",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern HackerRank-inspired styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #00EA64;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #A0AEC0;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #1A202C;
        border-left: 5px solid #00EA64;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .badge-matched {
        background-color: #1C4532;
        color: #68D391;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }
    .badge-missing {
        background-color: #742A2A;
        color: #FEB2B2;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Default HackerRank SDE Intern JD Preset
DEFAULT_HACKERRANK_JD = """HackerRank Software Development Engineer Intern (Bengaluru, 6-Month Full-time Onsite)
Overview:
HackerRank helps companies like NVIDIA, Amazon, and Microsoft hire and upskill the next generation of developers based on skills, not pedigree.
Software has entered an era where humans and AI build side by side. As this shift accelerates, the definition of strong technical talent is changing.

Requirements & Principles:
- Care about the craft: From the code we ship to the words we use, small details add up.
- Developers first: Every decision gets one test: does it help developers do their best work?
- Technical Skills: Strong foundation in Data Structures, Algorithms, Python, C++, or Java, REST APIs, Git, Automated Testing, and System Design concepts.
- Building side-by-side with AI tools (Gemini, Copilot, LangChain).
- Data-driven engineering, high standards, ownership, and transparent communication."""

DEFAULT_SAMPLE_RESUME = """Karthik Vangapandu
Email: karthik.v@example.com | Phone: +91 9876543210 | GitHub: github.com/karthik
Location: Bengaluru, India

Summary:
Motivated Computer Science student passionate about web development and coding. Looking for an SDE Internship opportunity.

Technical Skills:
Languages: Python, JavaScript, HTML/CSS, SQL
Tools & Frameworks: Git, React, Node.js, Express, MySQL

Experience:
Web Developer Intern | Tech Solutions (Jan 2024 - May 2024)
- Developed frontend components using React.
- Wrote backend APIs in Node.js and SQL queries.
- Used Git for version control.

Projects:
Automated Scripting Tool (Python)
- Wrote Python scripts to scrape website data and format into CSV files.
- Used basic error handling.

Web App for Task Management (React, Node.js)
- Created a task tracker app with user authentication and database storage.

Education:
B.Tech in Computer Science & Engineering (2023 - 2027)
ABC Institute of Technology, CGPA: 8.5/10
"""

# Header
st.markdown('<div class="main-title">⚡ AI Resume Architect & ATS Tailor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by <b>LangChain</b> + <b>Ollama (Local LLMs)</b> + <b>PyPDF</b> for HackerRank SDE Intern Role</div>', unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("⚙️ Configuration")
model_option = st.sidebar.selectbox("Select Ollama LLM Model", ["qwen2.5:latest", "gemma3:4b", "gemma3:1b"], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Input Sources")

uploaded_file = st.sidebar.file_uploader("Upload Existing Resume (PDF)", type=["pdf"])
use_sample_resume = st.sidebar.checkbox("Use Sample Resume", value=(uploaded_file is None))

st.sidebar.markdown("---")
st.sidebar.info("💡 **HackerRank SDE Intern Presets Loaded**\n- PyPDF Text Extraction\n- Agent 1: ATS Audit Chain\n- Agent 2: STAR Tailor Chain\n- ReportLab ATS PDF Export")

# Resume Text Extraction
resume_text = ""
if uploaded_file is not None:
    with st.spinner("Extracting text from uploaded PDF resume using PyPDF..."):
        try:
            pdf_bytes = uploaded_file.read()
            resume_text = extract_text_from_pdf(pdf_bytes)
            st.sidebar.success(f"PDF parsed: {len(resume_text)} characters extracted")
        except Exception as e:
            st.sidebar.error(f"Error reading PDF: {e}")
elif use_sample_resume:
    resume_text = DEFAULT_SAMPLE_RESUME

# Main UI Columns
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📄 Candidate Resume Input")
    resume_text_area = st.text_area("Parsed/Raw Resume Text", value=resume_text, height=350)

with col_right:
    st.subheader("🎯 Target Job Description (JD)")
    jd_text_area = st.text_area("Paste JD Text", value=DEFAULT_HACKERRANK_JD, height=350)

st.markdown("---")

# Action Button
if st.button("🚀 Run 2-Agent AI Workflow (Analyze & Tailor)", type="primary", use_container_width=True):
    if not resume_text_area.strip() or not jd_text_area.strip():
        st.warning("Please provide both Resume Text and Job Description text.")
    else:
        # Initialize session state for workflow outputs
        st.session_state["workflow_completed"] = False
        
        # Step 1: Run Agent 1
        with st.status("🧠 Executing Agent 1: ATS Match & Skill Gap Audit...", expanded=True) as status:
            st.write(f"Connecting to Ollama model `{model_option}` via LangChain...")
            ats_result = analyze_resume_ats(resume_text_area, jd_text_area, model_name=model_option)
            st.session_state["ats_result"] = ats_result
            status.update(label="✅ Agent 1 Audit Complete!", state="complete", expanded=False)

        # Step 2: Run Agent 2
        with st.status("✍️ Executing Agent 2: Resume Architect & STAR Optimizer...", expanded=True) as status:
            st.write("Rewriting bullet points, strengthening impact, and integrating missing keywords...")
            tailored_result = tailor_resume(resume_text_area, jd_text_area, ats_result, model_name=model_option)
            st.session_state["tailored_result"] = tailored_result
            status.update(label="✅ Agent 2 Optimization Complete!", state="complete", expanded=False)

        # Step 3: PDF Generation
        with st.status("🖨️ Compiling ATS PDF Resume using ReportLab...", expanded=True) as status:
            pdf_path = generate_resume_pdf(tailored_result, "hackerrank_tailored_resume.pdf")
            st.session_state["pdf_path"] = pdf_path
            status.update(label="✅ ATS PDF Resume Generated!", state="complete", expanded=False)

        st.session_state["workflow_completed"] = True

# Display Workflow Results in Tabs
if st.session_state.get("workflow_completed", False):
    st.success("🎉 Both AI Agents completed execution successfully!")
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Agent 1: ATS Gap Analysis",
        "📝 Agent 2: Tailored Resume",
        "⬇️ Download ATS PDF"
    ])

    ats_data = st.session_state.get("ats_result", {})
    tailored_data = st.session_state.get("tailored_result", {})
    pdf_filepath = st.session_state.get("pdf_path", "")

    # Tab 1: Agent 1 Outputs
    with tab1:
        score = ats_data.get("ats_score", 0)
        
        m_col1, m_col2 = st.columns([1, 2])
        with m_col1:
            st.metric(label="ATS Match Score", value=f"{score}%", delta=f"{score - 100}% gap")
            st.progress(score / 100.0)
        
        with m_col2:
            st.markdown("##### 📌 Matched Skills")
            for skill in ats_data.get("matched_skills", []):
                st.markdown(f'<span class="badge-matched">✓ {skill}</span>', unsafe_allow_html=True)
            
            st.markdown("<br/>##### ⚠️ Missing Keywords & Gaps", unsafe_allow_html=True)
            for skill in ats_data.get("missing_keywords", []):
                st.markdown(f'<span class="badge-missing">✗ {skill}</span>', unsafe_allow_html=True)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🚩 Weak Bullet Points Identified")
            for bullet in ats_data.get("weak_bullets", []):
                st.warning(f"• {bullet}")

        with c2:
            st.subheader("💚 HackerRank Cultural Alignment Notes")
            for note in ats_data.get("hackerrank_alignment", []):
                st.info(f"• {note}")

        st.subheader("💡 Key Recommendations")
        for rec in ats_data.get("key_recommendations", []):
            st.markdown(f"- {rec}")

    # Tab 2: Agent 2 Outputs
    with tab2:
        st.subheader("👤 Tailored Profile Overview")
        st.markdown(f"**Name:** {tailored_data.get('full_name')} | **Headline:** {tailored_data.get('headline')}")
        st.info(f"**Professional Summary:** {tailored_data.get('summary')}")

        st.markdown("---")
        st.subheader("🛠️ Categorized Skills")
        st.json(tailored_data.get("skills", {}))

        st.markdown("---")
        st.subheader("🚀 Optimized Experience & STAR Bullet Points")
        for exp in tailored_data.get("experience", []):
            st.markdown(f"#### {exp.get('title')} @ {exp.get('organization')}")
            st.caption(f"{exp.get('duration')} | {exp.get('location')}")
            for b in exp.get("bullet_points", []):
                st.markdown(f"- {b}")

        st.markdown("---")
        st.subheader("💻 Optimized Projects")
        for proj in tailored_data.get("projects", []):
            st.markdown(f"#### {proj.get('name')} (`{proj.get('tech_stack')}`)")
            for b in proj.get("bullet_points", []):
                st.markdown(f"- {b}")

    # Tab 3: PDF Download
    with tab3:
        st.subheader("🖨️ Ready to Submit ATS PDF Resume")
        st.write("Your tailored resume has been converted into an ATS-scannable single-page PDF formatted specifically for the HackerRank SDE Intern role.")
        
        if os.path.exists(pdf_filepath):
            with open(pdf_filepath, "rb") as f:
                pdf_data = f.read()
            st.download_button(
                label="📥 Download Tailored ATS PDF Resume",
                data=pdf_data,
                file_name=f"{tailored_data.get('full_name', 'Tailored').replace(' ', '_')}_HackerRank_Resume.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
