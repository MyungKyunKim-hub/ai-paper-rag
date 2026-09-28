from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


load_dotenv()


# 1. PDF 로드
pdf_loader = PyPDFLoader("data/transformer.pdf")
pdf_docs = pdf_loader.load()


# 2. Chunk 생성
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
    separators=["\n\n", "\n"],
)

texts = text_splitter.split_documents(pdf_docs)


# 3. Embedding 모델
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
)


# 4. Vector DB 생성
vectorstore = Chroma.from_documents(
    documents=texts,
    embedding=embeddings,
    collection_name="paper_rag_fastapi",
)


# 5. Retriever 생성
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 2}
)


# 6. LLM 생성
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
    max_output_tokens=300,
)


# 7. Prompt 생성
prompt = ChatPromptTemplate.from_template("""
다음 컨텍스트를 바탕으로 질문에 답변해주세요.

컨텍스트에 관련 정보가 없다면
"주어진 정보로는 답변할 수 없습니다."라고 답변해주세요.

컨텍스트:
{context}

질문:
{input}

답변:
""")


# 8. 검색 문서를 LLM에게 전달하는 Chain
combine_docs_chain = create_stuff_documents_chain(
    llm,
    prompt,
)


# 9. Retriever + LLM 연결
rag_chain = create_retrieval_chain(
    retriever,
    combine_docs_chain,
)


# 10. 질문 처리 함수
def ask_rag(question):

    response = rag_chain.invoke({
        "input": question
    })

    return response