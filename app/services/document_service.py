import os
import uuid
import shutil
from datetime import datetime, timezone
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.models.audit import Document
from app.core.config import settings

def _ensure_upload_dir() -> Path:
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path

class DocumentService:
    def upload_document(self, db: Session, entity_type: str, entity_id: str, title: str, file: UploadFile, uploaded_by: str) -> Document:
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit"
            )

        upload_dir = _ensure_upload_dir() / entity_type / entity_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = upload_dir / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc = Document(
            entity_type=entity_type,
            entity_id=entity_id,
            title=title,
            file_path=str(file_path),
            file_type=file.content_type
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def get_documents(self, db: Session, entity_type: str, entity_id: str):
        return db.query(Document).filter(
            Document.entity_type == entity_type,
            Document.entity_id == entity_id
        ).all()

    def get_document_by_id(self, db: Session, document_id: str) -> Document:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc

    def delete_document(self, db: Session, document_id: str):
        doc = self.get_document_by_id(db, document_id)
        file_path = Path(doc.file_path)
        if file_path.exists():
            file_path.unlink()
        db.delete(doc)
        db.commit()
        return {"message": "Document deleted successfully"}

document_service = DocumentService()
