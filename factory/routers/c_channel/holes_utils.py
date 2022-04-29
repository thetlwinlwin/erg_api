from pathlib import WindowsPath
from fastapi import UploadFile


async def saving_holes_image(file:UploadFile,path:WindowsPath):
    with path.open(mode='wb') as image:
        image.write(await file.read())