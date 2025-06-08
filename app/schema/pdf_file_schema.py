from pydantic import BaseModel

class PDFFileResponse(BaseModel):
    id: int
    file_name: str

    class Config:
        orm_mode = True
