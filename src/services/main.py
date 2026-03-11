from fastapi import FastAPI, UploadFile, File
from .query import ask_ques, generate_mcq
from .file_processor import process_uploaded_file

app = FastAPI()

@app.get("/")
def health_check():
    return {
        "status": "HEALTHY"
    }

@app.post("/query")
async def get_ans(ques: str):
    return {
        "answer": ask_ques(ques=ques)
    }

@app.post("/upload")
async def upload(file: UploadFile=File(...)):
    await process_uploaded_file(file=file)
    return {
        "message": "File uploaded successfully!"
    }

@app.post("/mcq")
async def gen_mcq():
    generate_mcq()
    return {
        "message": "OK"
    }