# SynapseAI

 [![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Built with FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-orange.svg)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
- [About SynapseAI](#about-synapseai)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Fallback Mechanism](#fallback-mechanism)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)



---

## About SynapseAI

SynapseAI is a cutting-edge, **fully local document question-answering system** designed for fast, contextual interactions with your offline documents. Built with a robust **RAG (Retrieval-Augmented Generation) architecture**, it empowers users to retrieve accurate information without relying on external cloud services or internet connectivity for its primary function.

This project focuses on delivering high-performance, private, and comprehensive document search capabilities right on your local machine, ensuring your data remains secure and accessible.

---

## Features

-   **Fully Local Operation:** Interact with your documents completely offline, ensuring **data privacy and security**.
-   **Real-Time Contextual Answers:** Leverage advanced RAG techniques to provide **fast and highly relevant answers** to your queries.
-   **Intelligent Fallback Mechanism:** Automatically triggers web scraping via **FireCrawl** when local information is insufficient, guaranteeing comprehensive responses.
-   **Modular Architecture:** Designed for **multi-turn, conversational interactions**, optimizing for relevance, speed, and seamless execution.
-   **Scalable Document Management:** Efficiently manage and search large volumes of local documents, ideal for personal knowledge bases or small team environments.

---

## Technologies Used

* [**Crew AI**](https://www.crewai.com/) - For orchestrating intelligent agents and multi-step workflows.
* [**Groq LLM**](https://groq.com/) - Powering **blazingly fast** and efficient language model inferences for rapid responses.
* [**FireCrawl**](https://firecrawl.dev/) - Utilized for intelligent and targeted web scraping within the fallback mechanism.
* **RAG Architecture** (Retrieval-Augmented Generation) - The core methodology enabling enhanced, context-aware question-answering.
* [**Qdrant**](https://qdrant.tech/) - Our chosen **Vector Database** for efficient similarity search and lightning-fast document retrieval.
* **Python** - The primary programming language, offering flexibility and a rich ecosystem.
* [**LangChain**](https://www.langchain.com/) - A powerful framework for developing sophisticated LLM-powered applications.
* [**FastAPI**](https://fastapi.tiangolo.com/) - For building robust, high-performance, and easy-to-use APIs.

---

## Fallback Mechanism

SynapseAI incorporates a unique and intelligent **fallback mechanism** to ensure comprehensive answers. If the system determines that the local document base does not contain sufficient information to answer a user's query comprehensively, it seamlessly integrates with **FireCrawl** to perform targeted web scraping. This ensures that even for complex or niche queries, users receive accurate and complete answers by dynamically incorporating external, real-time sources without any manual intervention. This hybrid approach guarantees both privacy for local data and accuracy for broader queries.

---

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yash25112003/SynapseAI.git](https://github.com/yash25112003/SynapseAI.git)
    cd SynapseAI
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory of your project. This file will securely store your API keys and other configurations.
    ```
    GROQ_API_KEY=your_groq_api_key_here
    FIRECRAWL_API_KEY=your_firecrawl_api_key_here
    # Add paths to your local document storage, e.g.:
    # LOCAL_DOC_PATH=/path/to/your/documents
    ```
    **Note:** Replace `your_groq_api_key_here` and `your_firecrawl_api_key_here` with your actual API keys. You'll obtain these from the respective service providers.

---

## Usage

Once installed, SynapseAI provides a powerful API to interact with your documents. Here's a quick guide:

1.  **Start the FastAPI server:**
    This will launch the backend API.
    ```bash
    uvicorn main:app --reload
    ```
    You should see output indicating the server is running, typically on `http://127.0.0.1:8000`.

2.  **Access the API Interface:**
    Open your web browser and navigate to `http://127.0.0.1:8000/docs`. This will take you to the interactive Swagger UI, where you can explore available endpoints, test queries, and understand the API structure.

3.  **Upload and Index Your Documents:**
    Before querying, you need to add your documents to the system.
    * Place your documents (e.g., PDFs, `.txt` files, markdown files) into the directory specified in your `LOCAL_DOC_PATH` environment variable (if configured, otherwise use the default document ingestion endpoint).
    * Use the `/index_documents` endpoint in the Swagger UI (or a dedicated script) to process and index these documents into Qdrant. This step builds the local knowledge base.

4.  **Start Querying Your Documents!**
    Use the `/query` endpoint in the Swagger UI or make direct API calls to ask questions against your indexed documents.

    **Example API Request (using `curl`):**
    ```bash
    curl -X POST "[http://127.0.0.1:8000/query](http://127.0.0.1:8000/query)" \
         -H "Content-Type: application/json" \
         -d '{
               "question": "What are the main features of the RAG architecture?",
               "conversation_history": []
             }'
    ```

    **Example Response (simplified):**
    ```json
    {
      "answer": "The main features of the RAG architecture include combining retrieval of relevant documents with a generative language model to provide contextual and accurate answers...",
      "source_type": "local_document",
      "sources": ["document_1.pdf", "article_on_rag.txt"]
    }
    ```
    If the fallback mechanism is triggered, `source_type` might indicate `web_scrape` and `sources` would list URLs from FireCrawl.
