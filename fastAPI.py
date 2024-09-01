from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import Optional                                                             
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(file.file.read())
    
    return {"filename": file.filename}

@app.get("/uploads/{filename}")
async def get_file(filename: str):
    file_location = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.isfile(file_location):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_location)
                                                                                                                                        

# uvicorn fastAPI:app --reload
# curl -X POST "http://127.0.0.1:8000/upload/" -F "file=@C:/Users/Moiz Arain/Desktop/Fast API/uploads/Muhammad Ali Jinnah.jpg"
