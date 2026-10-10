import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, ListFlowable, ListItem

def generate_resume_pdf(tailored_data: dict, output_filepath: str = "tailored_resume.pdf") -> str:
    """
    Generates an ATS-optimized PDF resume using ReportLab based on the structured JSON data.
    """
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Clean ATS Typography Palette & Styles
    PRIMARY_COLOR = colors.HexColor("#1A365D")  # Deep Navy Blue
    TEXT_COLOR = colors.HexColor("#2D3748")     # Charcoal Text
    SECONDARY_COLOR = colors.HexColor("#4A5568") # Cool Gray

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        alignment=0, # Left
        spaceAfter=2
    )

    headline_style = ParagraphStyle(
        'DocHeadline',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=SECONDARY_COLOR,
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        'ContactLine',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=TEXT_COLOR,
        spaceAfter=8
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=PRIMARY_COLOR,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=TEXT_COLOR,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=TEXT_COLOR,
        spaceAfter=2
    )

    bold_bullet_prefix = ParagraphStyle(
        'BoldPrefix',
        parent=bullet_style,
        fontName='Helvetica-Bold'
    )

    # 1. Header (Name, Headline, Contact)
    name = tailored_data.get("full_name", "Candidate Name")
    story.append(Paragraph(name, title_style))

    headline = tailored_data.get("headline", "Software Development Engineer")
    story.append(Paragraph(headline, headline_style))

    contact_info = tailored_data.get("contact", {})
    contact_parts = []
    for key in ["email", "phone", "location", "github", "linkedin"]:
        val = contact_info.get(key)
        if val:
            contact_parts.append(val)
    contact_str = " | ".join(contact_parts)
    story.append(Paragraph(contact_str, contact_style))

    # Divider Line
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=8, spaceBefore=2))

    # 2. Professional Summary
    summary = tailored_data.get("summary")
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 4))

    # 3. Technical Skills
    skills_dict = tailored_data.get("skills", {})
    if skills_dict:
        story.append(Paragraph("TECHNICAL SKILLS", section_heading))
        skills_text_parts = []
        for cat, skill_list in skills_dict.items():
            if isinstance(skill_list, list):
                skills_str = ", ".join(skill_list)
            else:
                skills_str = str(skill_list)
            skills_text_parts.append(f"<b>{cat}:</b> {skills_str}")
        skills_combined = "<br/>".join(skills_text_parts)
        story.append(Paragraph(skills_combined, body_style))
        story.append(Spacer(1, 4))

    # 4. Experience
    experience_list = tailored_data.get("experience", [])
    if experience_list:
        story.append(Paragraph("EXPERIENCE", section_heading))
        for exp in experience_list:
            role = exp.get("title", "")
            org = exp.get("organization", "")
            dur = exp.get("duration", "")
            loc = exp.get("location", "")
            
            exp_header = f"<b>{role}</b> — <i>{org}</i>"
            exp_meta = f"<i>{dur} | {loc}</i>" if loc else f"<i>{dur}</i>"
            
            # Format header in a clean 2-column table layout
            meta_para = Paragraph(f"<font color='{SECONDARY_COLOR.hexval()}'>{exp_meta}</font>", ParagraphStyle('RightMeta', parent=body_style, alignment=2))
            header_para = Paragraph(exp_header, body_style)
            
            t = Table([[header_para, meta_para]], colWidths=[5.0*inch, 2.5*inch])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            story.append(t)

            bullets = exp.get("bullet_points", [])
            for b in bullets:
                story.append(Paragraph(f"• {b}", bullet_style))
            story.append(Spacer(1, 4))

    # 5. Key Projects
    projects_list = tailored_data.get("projects", [])
    if projects_list:
        story.append(Paragraph("PROJECTS", section_heading))
        for proj in projects_list:
            p_name = proj.get("name", "")
            p_stack = proj.get("tech_stack", "")
            proj_header = f"<b>{p_name}</b>"
            if p_stack:
                proj_header += f" <font color='{SECONDARY_COLOR.hexval()}'>| {p_stack}</font>"
            story.append(Paragraph(proj_header, body_style))

            bullets = proj.get("bullet_points", [])
            for b in bullets:
                story.append(Paragraph(f"• {b}", bullet_style))
            story.append(Spacer(1, 4))

    # 6. Education
    edu_list = tailored_data.get("education", [])
    if edu_list:
        story.append(Paragraph("EDUCATION", section_heading))
        for edu in edu_list:
            degree = edu.get("degree", "")
            inst = edu.get("institution", "")
            yr = edu.get("year", "")
            edu_str = f"<b>{degree}</b> — {inst} <font color='{SECONDARY_COLOR.hexval()}'>({yr})</font>"
            story.append(Paragraph(edu_str, body_style))

    # Build PDF
    doc.build(story)
    return os.path.abspath(output_filepath)

if __name__ == "__main__":
    sample_data = {
        "full_name": "Karthik Vangapandu",
        "headline": "Software Development Engineer Intern",
        "contact": {
            "email": "karthik@example.com",
            "phone": "+91 9876543210",
            "github": "github.com/karthik",
            "linkedin": "linkedin.com/in/karthikvangapandu",
            "location": "Bengaluru, India"
        },
        "summary": "Passionate software engineer skilled in Python, C++, Java, data structures, algorithms, REST APIs, and automated testing. Dedicated to building high-craft developer tools.",
        "skills": {
            "Languages": ["Python", "C++", "Java", "JavaScript"],
            "Frameworks & Tools": ["React", "Node.js", "REST APIs", "Git", "Automated Testing"],
            "Core CS": ["Data Structures", "Algorithms", "System Design"]
        },
        "experience": [
            {
                "title": "Software Engineering Intern",
                "organization": "Tech Solutions",
                "duration": "Jun 2024 - Present",
                "location": "Bengaluru, India",
                "bullet_points": [
                    "Engineered RESTful APIs with Node.js and Express, processing over 100k daily requests.",
                    "Automated integration testing pipelines using Python, increasing test coverage by 40%."
                ]
            }
        ],
        "projects": [
            {
                "name": "High-Throughput Data Pipeline",
                "tech_stack": "Python, Pandas, NumPy, Git",
                "bullet_points": [
                    "Built parallelized data processing scripts in Python, reducing runtime by 35%.",
                    "Integrated automated error logging and test suites to ensure 99.9% uptime."
                ]
            }
        ],
        "education": [
            {
                "degree": "B.Tech in Computer Science",
                "institution": "ABC Institute of Technology",
                "year": "2023 - 2027"
            }
        ]
    }

    output_pdf = generate_resume_pdf(sample_data, "test_resume.pdf")
    print(f"PDF successfully generated: {output_pdf}")
