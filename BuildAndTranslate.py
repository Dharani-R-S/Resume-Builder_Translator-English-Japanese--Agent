import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
import pdfplumber
from docx import Document
import io

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# ...rest of your code...

@st.cache_resource
def load_llm():
    return ChatGroq(temperature=0.3, model_name="llama3-8b-8192")

@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

llm = load_llm()
embedding = load_embedding_model()

# === Prompt Templates ===

keigo_prompt_template = PromptTemplate(
    input_variables=["text", "format", "hide_contact"],
    template="""
あなたは日本のプロのキャリアコンサルタントです。以下の英文の履歴書の内容を丁寧で適切な日本語（敬語）に翻訳してください。
{hide_contact}
特に職歴部分では、「〜を担当しました」「〜を行いました」「〜に従事しました」などの表現を用い、
適切な職務経歴書の形式に従ってください。
出力は日本の職務経歴書にふさわしい丁寧語や敬語を使ってください。
出力形式は{format}でお願いします。

### 英文内容:
{text}

### 出力（日本語の敬語・ビジネス文）:
""".strip()
)

casual_jp_template = PromptTemplate(
    input_variables=["text", "format", "hide_contact"],
    template="""
あなたは日本のキャリアアドバイザーです。以下の英文の履歴書の内容を自然な日本語（カジュアル）に翻訳してください。
{hide_contact}
職歴やスキルはわかりやすく簡潔にまとめてください。
出力形式は{format}でお願いします。

### 英文内容:
{text}

### 出力（日本語のカジュアル文）:
""".strip()
)

en_resume_template = PromptTemplate(
    input_variables=["text", "format", "hide_contact"],
    template="""
You are a resume-writing assistant for job applicants.
Refine the resume content below to use a professional tone in English, improving clarity, structure, and grammar without changing the meaning.
{hide_contact}
Output format: {format}

### Original:
{text}

### Improved Resume (Professional English):
""".strip()
)

concise_en_template = PromptTemplate(
    input_variables=["text", "format", "hide_contact"],
    template="""
You are a resume assistant. Rewrite the following resume in concise, bullet-point English, focusing on achievements and skills.
{hide_contact}
Output format: {format}

### Original:
{text}

### Concise Resume:
""".strip()
)

linkedin_en_template = PromptTemplate(
    input_variables=["text", "format", "hide_contact"],
    template="""
You are a LinkedIn profile expert. Rewrite the following resume as a LinkedIn summary and experience section, using a friendly and professional English tone.
{hide_contact}
Output format: {format}

### Original:
{text}

### LinkedIn Profile:
""".strip()
)

# === Streamlit App ===
st.set_page_config(page_title="🌐 Multilingual Resume Builder & Translator", layout="wide")

# --- Sidebar Navigation ---
st.sidebar.title("🌐 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Resume Builder", "About"],
    index=1
)

if page == "Home":
    st.title("🌐 Multilingual Resume Builder & Translator")
    st.markdown("""
    Welcome!  
    This Agent helps you build, refine, and translate your resume between English 🇬🇧 and Japanese 🇯🇵 with a professional tone.
    
    - **Build** your resume section by section  
    - **Refine** and **translate** with AI  
    - **Import** your resume as PDF  
    - **Export** your resume in various formats  
    """)
    st.info("Use the sidebar to navigate to the Resume Builder.")

elif page == "Resume Builder":
    st.title("📝 Resume Builder & Translator (English - Japanese)")
    st.write("Fill in your details below, or upload your existing resume to enhance, translate, and refine it.")

    # --- Language and Style Controls ---
    st.markdown("#### 1. Language & Output Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        input_language = st.selectbox("Input Language", ["English", "Japanese"], key="input_language")
    with col2:
        output_style = st.selectbox(
            "Output Style",
            [
                "Japanese Keigo (Polite)",
                "Japanese Casual",
                "English Professional",
                "English Concise",
                "English for LinkedIn"
            ],
            key="output_style"
        )
    with col3:
        output_format = st.selectbox("Output Format", ["Markdown", "Plain Text"], key="output_format")

    st.markdown("---")

    # --- Resume File Upload Section ---
    st.markdown("#### 2. Upload Your Resume (PDF Only)")
    uploaded_file = st.file_uploader("Choose a resume file", type=["pdf"])
    uploaded_resume_text = ""
    if uploaded_file is not None:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                uploaded_resume_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            st.error(f"Error reading PDF file: {e}")

        if uploaded_resume_text.strip():
            st.success("Resume text extracted! You can now edit or use it below.")
            extracted_text = st.text_area("Extracted Resume", value=uploaded_resume_text, height=300, key="uploaded_resume_text_area")
            if st.button("Use Extracted Text"):
                st.session_state["resume_input"] = extracted_text
                st.success("Extracted text loaded into the main editor below!")

    st.markdown("---")

    # --- Section counts in session_state ---
    st.markdown("#### 3. Resume Sections (Manual Entry)")
    if "num_jobs" not in st.session_state:
        st.session_state["num_jobs"] = 1
    if "num_projects" not in st.session_state:
        st.session_state["num_projects"] = 0
    if "num_edu" not in st.session_state:
        st.session_state["num_edu"] = 1

    colj, colp, cole = st.columns(3)
    with colj:
        num_jobs = st.number_input("How many jobs?", min_value=1, max_value=10, value=st.session_state["num_jobs"], key="num_jobs_input")
    with colp:
        num_projects = st.number_input("How many projects?", min_value=0, max_value=10, value=st.session_state["num_projects"], key="num_projects_input")
    with cole:
        num_edu = st.number_input("How many education entries?", min_value=1, max_value=5, value=st.session_state["num_edu"], key="num_edu_input")

    if st.button("Update Sections"):
        st.session_state["num_jobs"] = num_jobs
        st.session_state["num_projects"] = num_projects
        st.session_state["num_edu"] = num_edu
        st.rerun()

    st.markdown("---")

    # === Input Area ===
    with st.form("resume_form"):
        st.markdown("#### 4. Enter Your Resume Details (Manual)")

        name = st.text_input("Full Name", key="name")
        email = st.text_input("Email", key="email")
        phone = st.text_input("Phone", key="phone")
        linkedin = st.text_input("LinkedIn URL", key="linkedin")
        summary = st.text_area("Professional Summary", key="summary")

        # Dynamic Work Experience
        st.markdown("##### Work Experience")
        jobs = []
        for i in range(st.session_state["num_jobs"]):
            with st.expander(f"Job #{i+1}"):
                job_title = st.text_input("Job Title", key=f"job_title_{i}")
                job_company = st.text_input("Company", key=f"job_company_{i}")
                job_dates = st.text_input("Dates", key=f"job_dates_{i}")
                job_desc = st.text_area("Description", key=f"job_desc_{i}")
                jobs.append({
                    "title": job_title,
                    "company": job_company,
                    "dates": job_dates,
                    "desc": job_desc
                })

        # Dynamic Projects
        st.markdown("##### Projects")
        projects = []
        for i in range(st.session_state["num_projects"]):
            with st.expander(f"Project #{i+1}"):
                proj_title = st.text_input("Project Title", key=f"proj_title_{i}")
                proj_desc = st.text_area("Project Description", key=f"proj_desc_{i}")
                projects.append({
                    "title": proj_title,
                    "desc": proj_desc
                })

        # Dynamic Education
        st.markdown("##### Education")
        education = []
        for i in range(st.session_state["num_edu"]):
            with st.expander(f"Education #{i+1}"):
                edu_degree = st.text_input("Degree", key=f"edu_degree_{i}")
                edu_school = st.text_input("School", key=f"edu_school_{i}")
                edu_dates = st.text_input("Dates", key=f"edu_dates_{i}")
                education.append({
                    "degree": edu_degree,
                    "school": edu_school,
                    "dates": edu_dates
                })

        skills = st.text_area("Skills (comma separated)", key="skills")
        certifications = st.text_area("Certifications", key="certifications")
        languages = st.text_area("Languages", key="languages")

        submitted = st.form_submit_button("Generate Resume")

    if submitted:
        # Assemble resume string
        resume_input = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nLinkedIn: {linkedin}\n\n"
        resume_input += f"Professional Summary:\n{summary}\n\n"

        resume_input += "Work Experience:\n"
        for job in jobs:
            resume_input += f"{job['title']} – {job['company']}\n{job['dates']}\n{job['desc']}\n\n"

        if projects:
            resume_input += "Projects:\n"
            for proj in projects:
                resume_input += f"{proj['title']}\n{proj['desc']}\n\n"

        resume_input += "Education:\n"
        for edu in education:
            resume_input += f"{edu['degree']} – {edu['school']}\n{edu['dates']}\n\n"

        resume_input += f"Skills:\n{skills}\n\n"
        resume_input += f"Certifications:\n{certifications}\n\n"
        resume_input += f"Languages:\n{languages}\n"

        st.session_state["resume_input"] = resume_input
        st.success("Resume assembled! Now choose output style and translate/refine below.")

    st.markdown("---")
    st.markdown("#### 5. Paste, Edit, or Enhance Resume Content")
    resume_input = st.text_area(
        "Paste your Resume Content Here",
        value=st.session_state.get("resume_input", ""),
        height=300
    )

    hide_contact = st.checkbox("Hide Contact Info (Name, Email, Phone, LinkedIn)", key="hide_contact")

    if st.button("🔁 Translate & Refine"):
        if not resume_input.strip():
            st.warning("Please enter your resume content first.")
        else:
            with st.spinner("Translating & Refining with Groq..."):
                # Hide contact info if selected
                hide_contact_str = (
                    "Do not include any contact information such as name, email, phone, or LinkedIn in the output."
                    if hide_contact else ""
                )

                # Choose appropriate prompt
                prompt = ""
                if output_style == "Japanese Keigo (Polite)":
                    prompt = keigo_prompt_template.format(
                        text=resume_input,
                        format=output_format,
                        hide_contact=hide_contact_str
                    )
                elif output_style == "Japanese Casual":
                    prompt = casual_jp_template.format(
                        text=resume_input,
                        format=output_format,
                        hide_contact=hide_contact_str
                    )
                elif output_style == "English Professional":
                    prompt = en_resume_template.format(
                        text=resume_input,
                        format=output_format,
                        hide_contact=hide_contact_str
                    )
                elif output_style == "English Concise":
                    prompt = concise_en_template.format(
                        text=resume_input,
                        format=output_format,
                        hide_contact=hide_contact_str
                    )
                elif output_style == "English for LinkedIn":
                    prompt = linkedin_en_template.format(
                        text=resume_input,
                        format=output_format,
                        hide_contact=hide_contact_str
                    )
                else:
                    prompt = resume_input  # fallback

                # Call Groq LLM via LangChain
                response = llm.invoke(prompt if isinstance(prompt, str) else prompt.to_string())
                output_text = response.content if hasattr(response, "content") else str(response)

                st.success("✅ Translation Completed")
                st.subheader("📄 Refined Resume Output")
                st.markdown(
                    f"<div style='white-space: pre-wrap; font-family: monospace;'>{output_text}</div>",
                    unsafe_allow_html=True
                )
                st.download_button("⬇️ Download as .txt", data=output_text, file_name="refined_resume.txt")

elif page == "About":
    st.title("About")
    st.markdown("""
    **Resume Builder & Translator**  
    - Powered by [Groq](https://groq.com/), [LangChain](https://www.langchain.com/), and [LlamaIndex](https://www.llamaindex.ai/)
    - Built with ❤️ by Dharani.
    - [GitHub Repo](#) (https://github.com/Dharani-R-S)
    """)

st.markdown("---")
st.markdown("Made with ❤️ by Dharani. R. S., © 2025")