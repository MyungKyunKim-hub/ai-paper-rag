# AI Paper RAG

AI 논문 PDF를 업로드하고 논문 내용에 대해 질문할 수 있는 RAG 기반 QA 서비스입니다.

PDF 문서를 Chunk 단위로 분할한 뒤 BGE-M3로 Embedding하고,
Chroma Vector DB에서 관련 문서를 검색하여 Gemini가 답변을 생성하도록 구현했습니다.

단순히 RAG를 구현하는 것에서 끝내지 않고,
Chunk Size / Overlap / Retriever k 값을 변경하면서 검색 정확도와 답변 정확도를 비교했습니다.

이후 RAG 로직을 별도로 분리하고 FastAPI REST API와 PostgreSQL을 연동했으며,
Docker를 이용해 FastAPI 기반 RAG API를 컨테이너 환경에서 실행했습니다.


## Demo

배포된 서비스: [AI Paper RAG Demo](https://ai-paper-rag-jo67xxiki97pd478npaegh.streamlit.app/)

Streamlit을 이용하여 논문 PDF를 업로드하고 질문을 입력하면
답변과 관련 출처를 확인할 수 있는 UI를 구현했습니다.


## RAG 구조

PDF

→ Text Split

→ BGE-M3 Embedding

→ Chroma Vector DB

→ Retriever

→ Gemini

→ Answer


## Backend 구조

FastAPI를 이용해 기존 RAG 파이프라인을 API 형태로 호출할 수 있도록 구성했습니다.

POST /ask

→ 질문 입력

→ RAG Pipeline

→ 답변 생성

→ PostgreSQL 저장

→ JSON Response


GET /history

→ PostgreSQL

→ 질문 / 답변 기록 조회

→ JSON Response


## 사용 기술

- Python
- Streamlit
- LangChain
- ChromaDB
- BGE-M3
- Gemini
- FastAPI
- PostgreSQL
- Docker


## FastAPI / PostgreSQL

기존 RAG 검색 및 생성 로직을 별도의 함수로 분리하고,
FastAPI를 이용해 REST API를 구현했습니다.

### POST /ask

JSON으로 질문을 받아 RAG 파이프라인을 실행하고
생성된 답변을 반환합니다.

질문과 생성된 답변은 PostgreSQL에 저장하도록 구현했습니다.

### GET /history

PostgreSQL에 저장된 질문과 답변 기록을 조회하여
JSON 형태로 반환하도록 구현했습니다.

DB 접속 정보와 API Key 등의 민감 정보는 환경변수로 분리했습니다.


## Docker

FastAPI 기반 RAG API를 Docker 환경에서 실행할 수 있도록 구성했습니다.

Python 3.11 기반 이미지를 사용하고,
requirements.txt를 통해 필요한 라이브러리를 설치한 뒤
Uvicorn으로 FastAPI 서버가 실행되도록 Dockerfile을 작성했습니다.

Docker 이미지 생성 및 컨테이너 실행 후
로컬 환경에서 실제 RAG API 요청과 응답을 확인했습니다.

구현 과정에서 Python 라이브러리 버전 충돌과
컨테이너 환경변수 문제를 확인하고 해결했습니다.


## 추가 학습 / 실험

### LLM Tool Calling

LangChain Tool을 이용해 간단한 add / multiply Tool을 구현했습니다.

Gemini에 Tool 정보를 전달하고,
사용자의 질문에 따라 LLM이 사용할 Tool과 인자를 선택하는 과정을 확인했습니다.

LLM이 직접 Python 함수를 실행하는 것이 아니라,
LLM이 Tool Call을 생성하고 애플리케이션이 실제 Tool을 실행하는 구조를 실습했습니다.

### LangGraph

LangGraph의 State / Node / Edge 구조와
Agent 실행 흐름을 학습하기 위한 간단한 테스트 코드를 작성했습니다.

현재 프로젝트의 실제 RAG 서비스에는 LangGraph를 적용하지 않았으며,
기본적인 구조를 이해하기 위한 학습 코드입니다.


## 최종 RAG 설정

- Chunk Size: 1000
- Chunk Overlap: 100
- Retriever k: 2

여러 설정을 테스트하였고 최종 설정
Chunk Size=1000, Overlap=100, k=2에서
Retrieval Accuracy 93.33%, Answer Accuracy 90%를 기록했습니다.


### Chunk 실험 결과

| Chunk Size | Overlap | Retrieval Accuracy | Answer Accuracy |
| ----------: | ------: | -----------------: | --------------: |
| 500 | 50 | 90.00% | 75.00% |
| 500 | 100 | 93.33% | 80.00% |
| 800 | 100 | 90.00% | 76.67% |
| 1000 | 0 | 93.33% | 83.33% |
| 1000 | 100 | 93.33% | 90.00% |
| 1000 | 150 | 93.33% | 90.00% |

1000/100과 1000/150의 성능이 동일했기 때문에
Overlap이 더 작은 100을 최종값으로 선택했습니다.


### Retriever k 실험 결과

| k | Retrieval Accuracy | Answer Accuracy |
| -: | -----------------: | --------------: |
| 1 | 86.67% | 73.33% |
| 2 | 93.33% | 90.00% |
| 3 | 93.33% | 86.67% |
| 4 | 93.33% | 90.00% |
| 5 | 93.33% | 90.00% |

k=2 이후 검색 정확도가 증가하지 않았고,
답변 정확도 역시 추가적인 개선이 확인되지 않아 k=2를 선택했습니다.


## 구현하면서 해결한 문제

### Streamlit 재실행으로 인한 Vector DB 재생성

Streamlit은 사용자 입력이 발생할 때 전체 스크립트를 다시 실행하기 때문에
질문을 입력할 때마다 Chroma Vector DB가 다시 생성되는 문제가 있었습니다.

`st.session_state`에 Vector DB와 업로드한 PDF의 hash를 저장하고,
같은 PDF라면 기존 Vector DB를 재사용하도록 수정했습니다.


## Project Files

- `Streamlit.py` : Streamlit 기반 RAG UI
- `rag_service.py` : RAG 검색 및 답변 생성 로직
- `fastapi_app.py` : FastAPI REST API
- `db_service.py` : PostgreSQL 저장 및 조회
- `Dockerfile` : FastAPI RAG API Docker 환경
- `agent_test.py` : LLM Tool Calling 학습 코드
- `langgraph_test.py` : LangGraph 기본 구조 학습 코드
- `db_test.py` : PostgreSQL 연결 테스트 코드