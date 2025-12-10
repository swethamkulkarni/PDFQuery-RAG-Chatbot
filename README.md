<p align="center">
  <img src="https://img.shields.io/badge/AI-Chatbot-blue?style=for-the-badge&logo=appveyor" alt="AI Chatbot Badge"/>
  <img src="https://img.shields.io/badge/RAG-Powered-purple?style=for-the-badge&logo=read-the-docs" alt="RAG Badge"/>
  <img src="https://img.shields.io/badge/Streamlit-Frontend-orange?style=for-the-badge&logo=streamlit" alt="Streamlit Badge"/>
</p>

<h1 align="center">🤖 PDFQuery RAG Chatbot</h1>
<p align="center">An AI-powered assistant that answers employee questions about company policies using Retrieval-Augmented Generation (RAG).</p>
<!-- <p align="center">
  <img src="https://images.unsplash.com/photo-1590608897129-79b7e1c6ff8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" alt="Chatbot Banner" width="80%"/>
</p> -->

---

## 🎯 Project Goal

Build a chatbot that:

- Loads and processes a company policy PDF
- Splits, embeds, and stores text in a vector database
- Retrieves relevant passages and generates answers via an LLM
- Provides a simple Streamlit UI for employees during onboarding

---

## 🧰 Tech Stack & Tools

### Document Processing
- **PyPDF** – Loading and parsing PDFs  
- **LangChain** –  
  - RecursiveCharacterTextSplitter  
  - ChatPromptTemplate  
  - MessagesPlaceholder  
  - PyPDFLoader  
  - RunnablePassthrough  

### Embeddings & Vector Store
- **OpenAI Embeddings**  
- **ChromaDB** – Vector database for efficient retrieval  

### LLM
- **ChatGroq / LLaMA-3.3-70B Versatile**  
  (Initially tested with Mixtral; switched after token exhaustion)

### Frontend
- **Streamlit** – Simple UI for interacting with the chatbot  

### Observability
- **LangSmith** – Logging and debugging LLM requests

---

## ▶️ Running the Project Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/PDFQuery-RAG-Chatbot.git

2. **Add your environment variables (API keys)**
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
 4.**Run the app**
   ```bash
  streamlit run app.py
  ```

---

## 📘 What I Learned

- **RAG Integration:** Integrating an LLM with a retrieval pipeline end-to-end
- **PDF Handling:** Loading & splitting PDFs, embedding text, storing vectors
- **LangChain Usage:** Using runnables and prompt templates to structure chains
- **Frontend Skills:** Basics of Streamlit for a usable interface
- **Debugging:** Handling model limits and token usage efficiently
