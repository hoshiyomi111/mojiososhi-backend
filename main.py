from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import openai
import os
import tempfile
from docx import Document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    with open(tmp_path, "rb") as audio_file:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    text = result.text
    os.unlink(tmp_path)

    doc = Document()
    doc.add_paragraph(text)
    docx_path = tmp_path + ".docx"
    doc.save(docx_path)

    return {
        "text": text,
        "docx_path": docx_path
    }

@app.get("/download")
async def download(path: str):
    return FileResponse(path, filename="transcription.docx")

@app.get("/")
async def root():
    return {"message": "文字起こしAPIが起動中です"}
