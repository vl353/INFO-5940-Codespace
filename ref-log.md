# 📝 Reference Log
This document records the use of external resources, tools, and generative AI in this project.
## 🛠️ External sources and tools
* **Python 3**: The core programming language used for this application.
* **Streamlit**: The main framework used to build interactive web user interfaces.
* **LangChain**: A framework for orchestrating the Retrieval Enhanced Generation (RAG) process.
    * `langchain-openai`: Specifically designed for integrating OpenAI compatible models and embeddings.
    * `langchain-community`: A component used for community contributions, such as the PyPDFLoader document loader.
* **ChromaDB**: A memory vector database used to store document embeddings and perform similarity searches.
* **PyPDF**: A Python library used by PyPDFLoader to parse and extract text from PDF files.
* **OpenAI Python Library**: Used to initialize API clients.

## 🤖 GenAI usage
Throughout the development process, I used generative AI (Google's Gemini model) as a programming assistant, debugger, and consultant. My use of AI mainly focuses on the following aspects:
1. I used AI as a technical advisor to explore the possibilities of implementing new features and the advantages and disadvantages of different solutions, it assisted me in making the final technology selection.
2. When specific features needed to be added or removed (such as adding function of document content preview), I used AI assistance to quickly refactor and adjust the code.
3. When encountering Python dependency related 'ModulaNotFoundError' errors, I utilized AI to quickly locate potentially missing packages and obtain suggested repair commands significantly reduces debugging time.

