from fastapi import UploadFile, File
import aiofiles
from datetime import datetime

async def process_uploaded_file(file: UploadFile=File(...)):
    if(file.filename[-4:] != ".pdf"):
        print("Only supported file type: PDF")
        raise Exception("File type error: file is not a pdf file!")
    file_path = "../llm/data/" + str(datetime.now()) + "_data.pdf"
    try:
        # with open(file_path, "wb") as f:
        #     f.write(file)
        # print(f"File {file_path} saved successfully!")
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content) 
    except IOError as err:
        print(f"Error saving pdf file: {err}")
    

__all__ = ["process_uploaded_file"]