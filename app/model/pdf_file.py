from sqlalchemy import Column, Integer, String, LargeBinary
from app.database.db import Base

class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    file_name = Column(String, nullable=False)
    file_uploaded_timestamp = Column(String, nullable=True)
    file_data = Column(LargeBinary, nullable=False)
    analysis_status = Column(String, default="pending")  # <- NEW
