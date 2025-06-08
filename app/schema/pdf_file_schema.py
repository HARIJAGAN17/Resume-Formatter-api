from pydantic import BaseModel

class PDFFileResponse(BaseModel):
    id: int
    project_id: int
    file_name: str
    file_uploaded_timestamp: str
    file_data: str
    analysis_status: str  # <- NEW

    class Config:
        orm_mode = True
