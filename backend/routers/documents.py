from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ..database import db_manager
from ..services.ocr import ocr_service
from ..services.classifier import classifier_service
from .auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    contents = await file.read()
    
    # Process OCR and Classification
    text, error = ocr_service.extract_from_bytes(contents)
    if error:
        raise HTTPException(status_code=500, detail=f"OCR Error: {error}")
    
    category, confidence = classifier_service.classify(text)
    
    # Save to Database
    doc_id = db_manager.execute_query("""
        INSERT INTO Documents (id_user, nom_fichier, chemin_fichier, texte_extrait, categorie, score_confiance)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (current_user['id_user'], file.filename, f"uploads/{file.filename}", text, category, confidence))
    
    return {
        "id": doc_id,
        "filename": file.filename,
        "text": text,
        "category": category,
        "confidence": confidence
    }

@router.get("/")
async def list_documents(current_user: dict = Depends(get_current_user)):
    docs = db_manager.execute_query("SELECT * FROM Documents WHERE id_user = %s ORDER BY date_upload DESC", (current_user['id_user'],))
    return docs

@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    # Note: Stats route is now under /documents/stats due to prefix
    stats = db_manager.execute_query("""
        SELECT categorie, COUNT(*) as count 
        FROM Documents 
        WHERE id_user = %s 
        GROUP BY categorie
    """, (current_user['id_user'],))
    return stats
