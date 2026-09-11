import streamlit as st
from dotenv import load_dotenv
import hashlib

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


# 페이지 설정


st.set_page_config(
    page_title="AI Paper RAG",
    page_icon="📄"
)

load_dotenv()

st.title("📄 AI Paper RAG")
st.write("논문 PDF를 업로드하고 질문해보세요.")



# Session State 초기화


if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "file_hash" not in st.session_state:
    st.session_state.file_hash = None



# PDF 업로드


uploaded_file = st.file_uploader(
    "논문 PDF를 업로드하세요.",
    type=["pdf"]
)


if uploaded_file is not None:

    # PDF 파일 내용
    file_bytes = uploaded_file.getvalue()

    # 같은 PDF인지 확인하기 위한 hash
    current_file_hash = hashlib.md5(file_bytes).hexdigest()



    # 새로운 PDF일 때만 Vector DB 생성


    if st.session_state.file_hash != current_file_hash:

        with st.spinner("논문을 분석하고 있습니다..."):

            # PDF 저장
            with open("temp.pdf", "wb") as f:
                f.write(file_bytes)


            # PDF 로드
            pdf_loader = PyPDFLoader("temp.pdf")
            pdf_docs = pdf_loader.load()


            # Chunk 생성
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                length_function=len,
                separators=["\n\n", "\n"],
            )

            texts = text_splitter.split_documents(pdf_docs)


            # Embedding
            embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-m3",
            )


            # Vector DB
            vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=embeddings,
                collection_name="paper_rag_debug",
            )


            # Session State에 저장
            st.session_state.vectorstore = vectorstore
            st.session_state.file_hash = current_file_hash
            st.session_state.page_count = len(pdf_docs)
            st.session_state.chunk_count = len(texts)


        st.success("Vector DB 생성 완료!")



    # 기존 Vector DB 재사용


    if st.session_state.vectorstore is not None:

        st.success(
            f"PDF 준비 완료! "
            f"{st.session_state.page_count}페이지 / "
            f"{st.session_state.chunk_count}개 Chunk"
        )


        # Retriever
        retriever = st.session_state.vectorstore.as_retriever(
            search_kwargs={"k": 2}
        )

        llm = ChatGoogleGenerativeAI(
          model="gemini-3.1-flash-lite",
          temperature=0,
          max_output_tokens=300,
        )

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


         # 검색된 문서들을 Gemini에게 전달하는 Chain
        combine_docs_chain = create_stuff_documents_chain(
         llm,
         prompt,
        )


         # Retriever + Gemini 연결
        rag_chain = create_retrieval_chain(
         retriever,
         combine_docs_chain
        )


        # 질문 입력

        question = st.text_input(
            "논문에 대해 질문하세요."
        )

        if question:

         response = rag_chain.invoke({
          "input": question
        })

         st.subheader("답변")

         st.write(response["answer"])

         st.subheader("출처")

         for i, doc in enumerate(response["context"],1):
            page = doc.metadata.get("page")
            st.write(f"### 출처 {i}")

            if page is not None:
                title = f"출처 {i} - 페이지 {page + 1}"
            else:
               title = f"출처 {i}"

            with st.expander(title):
             st.write(doc.page_content)




