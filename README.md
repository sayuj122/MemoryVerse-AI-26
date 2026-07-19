# 🧠 MemoryVerse AI '26

### *Transforming Fragmented Academic Data into an Intelligent Knowledge Repository*

---

## 🎯 The Goal

Every student builds a massive digital footprint throughout their academic journey—certificates, scattered resumes, internship letters, and GitHub repositories accumulate across different drives, devices, and emails. **MemoryVerse AI** bridges this gap.

Instead of acting as a passive file bucket (like Google Drive), MemoryVerse AI is an **automatic career biographer**. It ingests fragmented data structures, automatically maps core skills and timeline insights using AI, index-stores them in a localized vector database, and synthesizes everything into a recruiter-ready, searchable professional identity page.

---

## 🛠️ Tech Stack & Architecture

MemoryVerse AI leverages a streamlined, low-latency stack designed for rapid deployment and maximum execution speed:

* **Interface & Frontend:** `Streamlit` (Python) for an immediate, high-fidelity dashboard UI.
* **Vector Engine & Storage:** `ChromaDB` running as a localized, zero-configuration embedded persistence instance.
* **AI Engine & Semantics:** Google Gemini (`gemini-2.5-flash`) via the official `google-genai` client for JSON-structured metadata parsing and comprehensive portfolio synthesis.
* **Ingestion Utilities:** `pypdf` for clean document text layer extraction and native REST integrations for live GitHub profile parsing.

---

## ⚡ Quick Setup & Installation

Follow these steps to run the complete production platform locally inside **VS Code** in under 2 minutes:

### 1. Initialize Your Environment

Open your VS Code terminal and isolate your dependencies using a Python virtual environment:

```bash
# Create the virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

```

### 2. Install Dependencies

```bash
# Install required libraries
pip install streamlit chromadb google-genai pypdf requests

```

### 3. Add Your Gemini API Key

You can pass your Google AI Studio Gemini API key to the application using **one** of the two methods below:

#### Method A: Directly in the Code File (Easiest for Fast Testing)

Open `app.py` in VS Code. Right at the top under the `# 1. SETUP & INITIALIZATION` header, paste your key directly into the variable:

```python
HARDCODED_KEY = "AIzaSyYourActualKeyHere"

```

> ⚠️ **Security Warning:** Remember to reset this placeholder back to `HARDCODED_KEY = "your-key-here"` before making your repository public or pushing final commits to GitHub!

#### Method B: Set via Terminal Environment Variables

Alternatively, you can inject the token directly through your terminal context:

* **Windows (CMD):** `set GEMINI_API_KEY="AIzaSyYourActualKeyHere"`
* **Windows (PowerShell):** `$env:GEMINI_API_KEY="AIzaSyYourActualKeyHere"`
* **Mac/Linux:** `export GEMINI_API_KEY="AIzaSyYourActualKeyHere"`

### 4. Launch the Server

```bash
streamlit run app.py

```

*The local development server will spin up instantly at `http://localhost:8501`.*

---

## 🎨 Key Design Decisions (Why This Architecture Wins)

> **Zero-Auth Sandbox System:** Built strictly for rapid review. The database initializes locally in your VS Code workspace (`./memoryverse_db`) with zero external database cloud tokens required.

* **The "Win-Condition" Metadata Enrichment:** Standard applications search matching keyword sub-strings. MemoryVerse AI routes incoming text chunks to Gemini to dynamically build a valid JSON schema with custom high-impact tag indices (e.g. `#Python`, `#Leadership`, `#2026`) before storing vectors, allowing for clean categorization blocks at a glance.
* **Intent-Based Search Routing:** Replacing rigid, literal folder queries. A reviewer can type *"Show my backend engineering experience"* and the vector space engine isolates documents based on semantic similarity map metrics rather than matching hard keywords.
* **One-Click Portfolio Generation:** Aggregates unstructured timeline assets dynamically out of ChromaDB, feeding it into a generation prompt to return a human-readable, recruiter-ready Markdown showcase sheet.

---

## 💼 Step-by-Step Test Guide for Reviewers

1. **Tab 1 - Ingestion:** Input the GitHub user profile `T-Sayuj` (or any public handle) to fetch real-time repositories, or drag and drop an academic resume PDF. Check the generated micro-badge layout.
2. **Tab 2 - Search:** Execute conversational queries like `"Instances where I demonstrated team management"` or `"Where have I worked with databases?"` to check semantic context extraction.
3. **Tab 3 - Showcase:** Click **Generate Public Identity** to instantly build the synthesized executive markdown summary ready for external presentation sharing.
