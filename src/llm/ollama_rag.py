from langchain_ollama import ChatOllama

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter as RCTS
from langchain.tools import tool
from langchain.agents import create_agent
from sentence_transformers import CrossEncoder

llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0.5,
    # other params...
)

embeddings = OllamaEmbeddings(model="nomic-embed-text")

docs_reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

def rerank_fn(ques, documents, top_k_arg=3):
    pairs = [(ques, doc.page_content) for doc in documents]
    pairs_scores = docs_reranker.predict(pairs)

    ranked_docs = sorted(
        zip(documents, pairs_scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [doc for doc, _ in ranked_docs[:top_k_arg]]

# @tool(response_format="content_and_artifact")
# def retrieve_ctx(ques: str):
#     """Retrieve information based on a question"""
#     print("TOOL CALLED")
#     retrieved_documents = vector_store.similarity_search(ques, k=5)

#     serial_output = "\n\n".join((
#         f"Source: {document.metadata}\n\nChunk content: {document.page_content}"
#         for document in retrieved_documents
#     ))
    
#     return serial_output, retrieved_documents

# tools = [retrieve_ctx]
# system_prompt = """
# You are a document question answering assistant.

# Rules:
# 1. ALWAYS call the retrieve_ctx tool before answering.
# 2. NEVER answer from your own knowledge.
# 3. Only answer using the retrieved context.
# 4. If the context does not contain the answer, say "I don't know...".
# """

# rag_agent = create_agent(
#     model=llm,
#     tools=tools,
#     system_prompt=system_prompt
# )

retriever_cache = {}

def ask_ques(ques: str) -> str:
    question = ques

    from pathlib import Path
    script_location = Path(__file__).parent.absolute()
    file_location = script_location / 'data'

    retriever = create_retriever(path=file_location) if retriever_cache == {} else retriever_cache["retriever"]

    documents = retriever.invoke(question)
    ranked_documents = rerank_fn(ques=question, documents=documents)

    context = "\n\n".join(doc.page_content for doc in ranked_documents)

    prompt_msg = f"""
    Answer the question only using the context below:

    Context:
    {context}

    Question:
    {question}
    If you don't find the answer in the context, simply answer: 'I don't know...'
    """

    ans = llm.invoke(prompt_msg)

    return f"\n\n {ans.content}"

# while True:
#     question = input("Please input your query: \n\n")

#     # for evt in rag_agent.stream(
#     #     {"message": [{"role": "user", "content": question}]},
#     #     stream_mode="values"
#     # ):
#     #     msg = evt["messages"][-1]

#     #     print("CONTENT:", msg.content)
#     #     print("TOOL CALLS:", msg.tool_calls)
#     documents = retriever.invoke(question)
#     ranked_documents = rerank_fn(ques=question, documents=documents)

#     context = "\n\n".join(doc.page_content for doc in ranked_documents)

#     prompt_msg = f"""
#     Answer the question only using the context below:

#     Context:
#     {context}

#     Question:
#     {question}
#     If you don't find the answer in the context, simply answer: 'I don't know...'
#     """

#     ans = llm.invoke(prompt_msg)

#     print(f"\n\nAnswer to your question:\n\n {ans.content}")

def create_retriever(path):
    vector_store = Chroma(
    collection_name="ollama_rag_db",
    embedding_function=embeddings,
    persist_directory="./chroma_ollama_db"
)

    dir = path

    doc_loader =  DirectoryLoader(dir, glob="**/*.*")
    documents = doc_loader.load()

    splitter = RCTS(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )

    splits = splitter.split_documents(documents)

    print(f"The document is splitted into {len(splits)} chunks successfully...")

    docs_ids = vector_store.add_documents(documents=splits)

    print(f"chunk ids: {docs_ids[:5]}")

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 10}
    )

    retriever_cache["retriever"] = retriever

    return retriever

def generate_mcq():
    response = ask_ques(f"Generate 10 MCQ questions & their answers based on the given context: Context: {'attention.pdf file'}")

    try:
        with open("mcq_dump.txt", "w") as f:
            f.write(response)
    except IOError as err:
        print(err)




__all__ = ["ask_ques", "generate_mcq"]

