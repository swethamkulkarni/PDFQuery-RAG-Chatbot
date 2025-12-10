# 🤖 PDFQuery RAG Chatbot

An AI-powered assistant built using **Retrieval-Augmented Generation (RAG)** that answers employee questions about company policies — saving HR teams time during the onboarding process.

This version uses the *Umbrella Corporation* policy PDFs as an example, but can be adapted to any organization’s documents.

---

## 🎯 Project Goal

Build a chatbot that:

- Loads and processes a company policy PDF
- Splits, embeds, and stores text in a vector database
- Retrieves relevant passages and generates answers via an LLM
- Provides a simple Streamlit UI for employees during onboarding

---

##  Tech Stack & Tools

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
   git clone https://github.com/swethamkulkarni/PDFQuery-RAG-Chatbot.git

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
