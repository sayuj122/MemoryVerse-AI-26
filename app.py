import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import pypdf
import requests
import os
import json
from google import genai
from google.genai import types

import streamlit as st
import os
from google import genai

# -----------------------------------------------------------------------------
# 1. SETUP & INITIALIZATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="MemoryVerse AI '26", page_icon="🧠", layout="wide")

# Check for API Key in environment variables
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 **Missing Gemini API Key!**")
    st.info("""
    To run this project, please set your Gemini API key in your terminal before launching Streamlit:
    
    * **Windows (CMD):** `set GEMINI_API_KEY="your-key-here"`
    * **Windows (PowerShell):** `$env:GEMINI_API_KEY="your-key-here"`
    * **Mac/Linux:** `export GEMINI_API_KEY="your-key-here"`
    
    Then restart your app using `streamlit run app.py`.
    """)
    st.stop()

# Initialize Gemini Client using the environment variable
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    st.stop()
# Initialize ChromaDB (Persistent local storage)
chroma_client = chromadb.PersistentClient(path="./memoryverse_db")

# Use Gemini embeddings via ChromaDB's default or a simple custom function wrapper
# To keep setup zero-config, we'll store texts with metadata and let Chroma handle lightweight defaults,
# or manually call Gemini embeddings if needed. For a fast hackathon, we use standard text storage + metadata queries.
collection = chroma_client.get_or_create_collection(name="user_digital_footprint")

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS (Ingestion & AI Processing)
# -----------------------------------------------------------------------------
def extract_text_from_pdf(file):
    """Extracts plain text from an uploaded PDF file."""
    pdf_reader = pypdf.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def fetch_github_repos(username):
    """Fetches public repository names and descriptions from GitHub."""
    url = f"https://api.github.com/users/{username}/repos"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            repos = response.json()
            repo_details = []
            for r in repos:
                desc = r['description'] if r['description'] else "No description provided."
                repo_details.append(f"Repo: {r['name']} - Description: {desc}")
            return "\n".join(repo_details)
        else:
            return None
    except Exception:
        return None

def generate_ai_metadata(text):
    """Uses Gemini to generate a 3-sentence summary and tags from raw text."""
    prompt = (
        "Analyze the following text from a student's document or profile. "
        "Provide your response strictly in valid JSON format with two keys:\n"
        "1. 'summary': A concise, high-impact 3-sentence summary of the achievements, roles, or skills found.\n"
        "2. 'tags': A list of 4-6 relevant tech skills, soft skills, or timeline years (e.g., ['Python', 'Leadership', '2026']).\n\n"
        f"Text:\n{text}"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        # Fallback if AI structural output fails
        return {
            "summary": "Document successfully processed and indexed.",
            "tags": ["Imported", "Academic"]
        }

# -----------------------------------------------------------------------------
# INTERFACE & LAYOUT
# -----------------------------------------------------------------------------
st.title("🧠 MemoryVerse AI '26")
st.subheader("Transforming fragmented academic data into an Intelligent Knowledge Repository")
st.markdown("---")

# Sidebar navigation
menu = ["📥 Data Ingestion", "🔍 Semantic Search", "💼 Live Portfolio"]
choice = st.sidebar.radio("Navigation", menu)

# -----------------------------------------------------------------------------
# STEP 1 & 2: DATA INGESTION PIPELINE & AI PROCESSING
# -----------------------------------------------------------------------------
if choice == "📥 Data Ingestion":
    st.header("Step 1 & 2: Feed Your Knowledge Base")
    st.caption("Upload documents (Resumes, Certificates, Letters) or pull your GitHub data.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Document Upload")
        uploaded_file = st.file_uploader("Upload PDF Documents", type=["pdf"])
        
        if st.button("Process Document") and uploaded_file is not None:
            with st.spinner("Extracting text and running Win-Condition AI mapping..."):
                raw_text = extract_text_from_pdf(uploaded_file)
                
                if raw_text.strip():
                    # Generate AI summary and tags
                    ai_data = generate_ai_metadata(raw_text)
                    
                    # Save to ChromaDB
                    doc_id = f"doc_{uploaded_file.name}_{len(collection.get()['ids'])}"
                    collection.add(
                        documents=[raw_text],
                        metadatas=[{
                            "source": uploaded_file.name,
                            "summary": ai_data["summary"],
                            "tags": ", ".join(ai_data["tags"]),
                            "type": "document"
                        }],
                        ids=[doc_id]
                    )
                    st.success(f"Successfully Indexed: {uploaded_file.name}")
                    st.json(ai_data)
                else:
                    st.error("Could not extract readable text from the PDF.")

    with col2:
        st.subheader("GitHub Integration")
        github_username = st.text_input("Enter GitHub Username", placeholder="e.g., tsayuj")
        
        if st.button("Sync GitHub Repositories") and github_username:
            with st.spinner("Fetching repositories and generating AI summary..."):
                repo_text = fetch_github_repos(github_username)
                
                if repo_text:
                    ai_data = generate_ai_metadata(repo_text)
                    doc_id = f"github_{github_username}"
                    
                    collection.add(
                        documents=[repo_text],
                        metadatas=[{
                            "source": f"GitHub ({github_username})",
                            "summary": ai_data["summary"],
                            "tags": ", ".join(ai_data["tags"]),
                            "type": "github"
                        }],
                        ids=[doc_id]
                    )
                    st.success(f"Successfully Indexed GitHub Profile for {github_username}!")
                    st.json(ai_data)
                else:
                    st.error("Failed to fetch data. Check the username or network.")

# -----------------------------------------------------------------------------
# STEP 3: SEMANTIC SEARCH INTERFACE
# -----------------------------------------------------------------------------
elif choice == "🔍 Semantic Search":
    st.header("Step 3: Ask Your Digital History Anything")
    st.caption("The AI queries your vector knowledge base to recall specific skills, experiences, and context.")

    query = st.text_input(
        "Enter search query", 
        placeholder="e.g., Show my backend engineering experience or instances where I demonstrated leadership"
    )

    if query:
        with st.spinner("Searching Vector Database..."):
            # Fetch database contents
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if results and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    doc = results['documents'][0][i]
                    meta = results['metadatas'][0][i]
                    
                    with st.expander(f"📍 Found in: **{meta['source']}**", expanded=True):
                        st.markdown(f"**AI Summary:** {meta['summary']}")
                        
                        # Display tags beautifully
                        tags = meta['tags'].split(", ")
                        tag_badges = " ".join([f"`{t}`" for t in tags])
                        st.markdown(f"**Tags:** {tag_badges}")
            else:
                st.info("No matching historical records found in your profile repository yet.")

# -----------------------------------------------------------------------------
# STEP 4: SHOWCASE PAGE (PORTFOLIO GENERATOR)
# -----------------------------------------------------------------------------
elif choice == "💼 Live Portfolio":
    st.header("Step 4: The Showcase Page (Generate Public Identity)")
    st.caption("Consolidates all your fragmented knowledge records into a clean, presentation-ready portfolio sheet.")

    if st.button("Generate Public Identity"):
        with st.spinner("Synthesizing records into unified portfolio..."):
            all_data = collection.get()
            
            if all_data and all_data['metadatas']:
                # Compile structural text inputs for Gemini to build a beautiful presentation portfolio
                context_blocks = []
                for meta in all_data['metadatas']:
                    context_blocks.append(f"Source: {meta['source']}\nSummary: {meta['summary']}\nTags: {meta['tags']}")
                
                combined_context = "\n\n".join(context_blocks)
                
                portfolio_prompt = (
                    "You are an expert executive builder. Take the following summaries and tags extracted from a "
                    "student's historical records, and synthesize them into a stunning, professional, and well-structured "
                    "Markdown Portfolio Page. Group them logically by Core Skills, Key Projects, and Evidence of Impact/Certifications. "
                    "Make it look ready to show a hiring manager.\n\n"
                    f"Student Career Fragments:\n{combined_context}"
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=portfolio_prompt
                )
                
                st.success("Public Professional Identity Live! 🎉")
                st.markdown("---")
                st.markdown(response.text)
            else:
                st.warning("Your digital footprint repository is currently empty. Please upload documents in the 'Data Ingestion' tab first.")
