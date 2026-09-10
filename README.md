# AI Paper RAG

## Demo

배포된 서비스: [AI Paper RAG Demo](https://ai-paper-rag-jo67xxiki97pd478npaegh.streamlit.app/)

논문 PDF를 업로드하고 논문 내용에 대해 질문할 수 있는 RAG 기반 QA 서비스입니다.

단순히 RAG를 구현하는 것에서 끝내지 않고, chunk size / overlap / retriever k 값을 변경하면서 검색 정확도와 답변 정확도를 비교했습니다.

Streamlit을 이용하여 논문 PDF를 업로드하고 질문을 입력하면 답변과 관련 출처를 확인할 수 있는 간단한 UI를 구현했습니다.

## RAG 구조

PDF
→ Text Split
→ BGE-M3 Embedding
→ Chroma Vector DB
→ Retriever
→ Gemini
→ Answer

## 사용 기술

* Python
* Streamlit
* LangChain
* ChromaDB
* BGE-M3
* Gemini

## 최종 설정

* Chunk Size: 1000
* Chunk Overlap: 100
* Retriever k: 2

여러 설정을 테스트 하였고 결과 최종 설정 Chunk Size=1000, Overlap=100, K=2에서 Retrieval Accuracy 93.33%, Answer Accuracy 90%를 기록했습니다.

### Chunk 실험 결과

| Chunk Size | Overlap | Retrieval Accuracy | Answer Accuracy |
| ---------: | ------: | -----------------: | --------------: |
|        500 |      50 |             90.00% |          75.00% |
|        500 |     100 |             93.33% |          80.00% |
|        800 |     100 |             90.00% |          76.67% |
|       1000 |       0 |             93.33% |          83.33% |
|       1000 |     100 |             93.33% |          90.00% |
|       1000 |     150 |             93.33% |          90.00% |

1000/100과 1000/150의 성능이 동일했기 때문에 overlap이 더 작은 100을 최종값으로 선택했습니다.

### Retriever k 실험 결과

|  k | Retrieval Accuracy | Answer Accuracy |
| -: | -----------------: | --------------: |
|  1 |             86.67% |          73.33% |
|  2 |             93.33% |          90.00% |
|  3 |             93.33% |          86.67% |
|  4 |             93.33% |          90.00% |
|  5 |             93.33% |          90.00% |

k=2 이후 검색 정확도가 증가하지 않았고, 답변 정확도 역시 개선되지 않아 k=2를 선택했습니다.

## 구현하면서 해결한 문제

Streamlit은 사용자 입력이 발생할 때 전체 스크립트를 다시 실행하기 때문에 질문을 입력할 때마다 Chroma Vector DB가 다시 생성되는 문제가 있었습니다.

`st.session_state`에 Vector DB와 업로드한 PDF의 hash를 저장하고, 같은 PDF라면 기존 Vector DB를 재사용하도록 수정했습니다.
