from fastapi import FastAPI
from .query import ask_ques

app = FastAPI()

@app.get("/")
def health_check():
    return {
        "status": "HEALTHY"
    }

@app.post("/query")
def get_ans(ques: str):
    return {
        "answer": ask_ques(ques=ques)
    }