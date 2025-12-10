<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PDFQuery RAG Chatbot — README</title>
    <style>
      :root{--bg:#0f1724;--card:#0b1220;--muted:#94a3b8;--accent:#7c3aed;--glass:rgba(255,255,255,0.02)}
      body{font-family:Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; margin:0; background:linear-gradient(180deg,#071029 0%, #071129 100%); color:#e6eef8; line-height:1.6}
      .container{max-width:900px;margin:48px auto;padding:28px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border-radius:12px;box-shadow:0 10px 30px rgba(2,6,23,0.6);border:1px solid rgba(255,255,255,0.03)}
      header{display:flex;align-items:center;gap:16px}
      .logo{width:64px;height:64px;border-radius:12px;background:linear-gradient(135deg,#3b82f6,#7c3aed);display:flex;align-items:center;justify-content:center;font-weight:700;color:white;font-size:20px}
      h1{margin:0;font-size:28px}
      p.lead{color:var(--muted);margin-top:8px}
      section{margin-top:22px}
      h2{font-size:18px;margin:0 0 8px 0}
      ul{margin:8px 0 0 20px}
      pre{background:rgba(255,255,255,0.02);padding:14px;border-radius:8px;overflow:auto;border:1px solid rgba(255,255,255,0.03);color:#dbeafe}
      code{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;font-size:13px}
      .tech-list{display:flex;flex-wrap:wrap;gap:8px}
      .chip{background:var(--glass);padding:8px 10px;border-radius:999px;border:1px solid rgba(255,255,255,0.02);color:var(--muted);font-weight:600}
      .run{margin-top:12px}
      .btn{display:inline-block;padding:10px 14px;border-radius:10px;background:linear-gradient(90deg,var(--accent),#2563eb);color:white;text-decoration:none;font-weight:600}
      footer{margin-top:28px;color:var(--muted);font-size:13px}
      .future-list{margin-top:6px}
    </style>
  </head>
  <body>
    <div class="container">
      <header>
        <div class="logo">PDF</div>
        <div>
          <h1>PDFQuery RAG Chatbot</h1>
          <p class="lead">An AI-powered assistant that answers employee questions about company policy documents using Retrieval-Augmented Generation (RAG).</p>
        </div>
      </header>

      <section>
        <h2>🎯 Project Goal</h2>
        <p>Build a chatbot that:</p>
        <ul>
          <li>Loads and processes a company policy PDF</li>
          <li>Splits, embeds, and stores text in a vector database</li>
          <li>Retrieves relevant passages and generates answers via an LLM</li>
          <li>Provides a simple Streamlit UI for employees during onboarding</li>
        </ul>
      </section>

      <section>
        <h2>🧠 Tech Stack &amp; Tools</h2>
        <div class="tech-list">
          <div class="chip">PyPDF (PDF loading)</div>
          <div class="chip">LangChain (splitter, prompt templates, runnables)</div>
          <div class="chip">OpenAI Embeddings</div>
          <div class="chip">ChromaDB (vector store)</div>
          <div class="chip">ChatGroq / LLaMA (LLM)</div>
          <div class="chip">LangSmith (request logging)</div>
          <div class="chip">Streamlit (frontend)</div>
        </div>

        <h3 style="margin-top:12px">Details</h3>
        <ul>
          <li>Document processing: <strong>PyPDF</strong> + <strong>LangChain</strong> utilities (RecursiveCharacterTextSplitter, PyPDFLoader, ChatPromptTemplate, MessagesPlaceholder, RunnablePassthrough).</li>
          <li>Embeddings: <strong>OpenAI</strong> embeddings to convert text into vector space.</li>
          <li>Vector DB: <strong>ChromaDB</strong> for retrieval.</li>
          <li>LLM: started testing with Groq Mixtral family, then moved to <strong>LLaMA-3.3-70B Versatile</strong> due to token/usage limits.</li>
          <li>Observability: <strong>LangSmith</strong> for logging/debugging LLM requests.</li>
        </ul>
      </section>

      <section>
        <h2>▶️ Running the Project Locally</h2>
        <ol>
          <li>Clone the repository:
            <pre><code>git clone https://github.com/YOUR_USERNAME/PDFQuery-RAG-Chatbot.git</code></pre>
          </li>
          <li>Add your environment variables (API keys, any paths).</li>
          <li>Install dependencies:
            <pre><code>pip install -r requirements.txt</code></pre>
          </li>
          <li>Run the app:
            <pre><code>streamlit run app.py</code></pre>
          </li>
        </ol>

        <div class="run">
          <a class="btn" href="#">Copy setup snippet</a>
        </div>
      </section>

      <section>
        <h2>📘 What I learned</h2>
        <ul>
          <li>How to integrate an LLM with a retrieval pipeline (RAG) and wire it end-to-end.</li>
          <li>Loading &amp; splitting PDFs, embedding text, and storing vectors in ChromaDB.</li>
          <li>Using LangChain runnables and prompt templates to structure the conversation chain.</li>
          <li>Streamlit basics for a usable frontend and LangSmith for logging.</li>
          <li>Debugging model usage and switching models when hitting token or cost limits.</li>
        </ul>
      </section>

      <section>
        <h2>🔮 Future Improvements</h2>
        <ul class="future-list">
          <li>Support for <strong>multiple PDFs</strong> and multi-file ingestion flows.</li>
          <li>Robust handling of <strong>messy, real-world PDFs</strong> (layouts, images, tables).</li>
          <li>Enhance the chatbot with configurable <strong>tone &amp; personality</strong> and memory.</li>
          <li>Improve UI/UX for conversational context, history, and user feedback.</li>
        </ul>
      </section>

      <section>
        <h2>📄 License &amp; Notes</h2>
        <p style="color:var(--muted)">This repository is a proof-of-concept / MVP. Be mindful of API-key security — do not commit secrets. Add a <code>.gitignore</code> to exclude <code>.env</code>, local vector stores, and other sensitive files.</p>
      </section>

      <footer>
        Built with ❤️ — want this exported as a standalone file or a GitHub-ready README.md as well? Replace <strong>YOUR_USERNAME</strong> in the clone URL and you're ready to push. 🚀
      </footer>
    </div>
  </body>
</html>
