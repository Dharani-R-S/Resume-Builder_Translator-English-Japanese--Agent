# 🌐 Resume Builder & Translator

A smart, AI-powered Streamlit app that helps you build, refine, and translate your resume between **English 🇬🇧** and **Japanese 🇯🇵**, using Groq’s LLaMA 3 model, LangChain, and Hugging Face embeddings.

---

## 🚀 Features

- ✍️ **Build** your resume section by section using a user-friendly interface  
- 📄 **Upload** existing resumes in PDF format  
- 🤖 **Refine** your resume using AI (professional tone, LinkedIn style, bullet-points, etc.)  
- 🌸 **Translate** resumes from English to Japanese with Keigo (敬語) or casual style  
- 💾 **Download** translated or enhanced resumes in plain text  
- 🔐 Option to **hide personal contact details**

---

## 🛠️ Tech Stack

| Layer        | Tech Used |
|--------------|-----------|
| Frontend     | [Streamlit](https://streamlit.io) |
| LLM Backend  | [LangChain](https://www.langchain.com) + [Groq API](https://groq.com) (LLaMA 3) |
| Embeddings   | [Hugging Face](https://huggingface.co) `sentence-transformers/all-MiniLM-L6-v2` |
| PDF Parsing  | `pdfplumber` |
| Prompt Templates | LangChain `PromptTemplate` |

---

## 🧠 LLM Capabilities

Prompt styles include:
- 🇯🇵 **Japanese Keigo** – formal, respectful style for job applications
- 🇯🇵 **Japanese Casual** – friendly, natural tone
- 🇬🇧 **English Professional** – grammatically correct, structured refinement
- 📋 **English Concise** – resume in achievement-based bullet points
- 💼 **LinkedIn Format** – resume as LinkedIn summary + experience

---

## 📦 Folder Structure

