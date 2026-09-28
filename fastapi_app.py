from fastapi import FastAPI
from pydantic import BaseModel
from rag_service import ask_rag
from db_service import save_qa, get_history

app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "RAG API is running"}


@app.post("/ask")
def ask(request: QuestionRequest):

    response = ask_rag(request.question)

    save_qa(
        request.question,
        response["answer"]
    )

    return {"answer": response["answer"]}

@app.get("/history")
def history():
    rows = get_history()

    return {
        "history": [
            {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "created_at": row[3]
            }
            for row in rows
        ]
    }