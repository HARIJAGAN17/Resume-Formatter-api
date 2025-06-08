from sqlalchemy import Column, Integer, String, LargeBinary
from app.database.db import Base  

class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_data = Column(LargeBinary, nullable=False)  # This stores the binary PDF content
