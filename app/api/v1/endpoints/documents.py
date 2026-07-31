from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(
    entity_type: str = Form(...),
    entity_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = document_service.upload_document(db, entity_type, entity_id, title, file, current_user.id)
    return {
        "id": doc.id,
        "title": doc.title,
        "entity_type": doc.entity_type,
        "entity_id": doc.entity_id,
        "file_type": doc.file_type,
        "created_at": doc.created_at
    }

@router.get("/{entity_type}/{entity_id}")
def get_entity_documents(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    docs = document_service.get_documents(db, entity_type, entity_id)
    return [{"id": d.id, "title": d.title, "file_type": d.file_type, "created_at": d.created_at} for d in docs]

@router.get("/download/{document_id}")
def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = document_service.get_document_by_id(db, document_id)
    file_path = Path(doc.file_path)
    if not file_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(path=str(file_path), filename=file_path.name, media_type=doc.file_type or "application/octet-stream")

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return document_service.delete_document(db, document_id)
