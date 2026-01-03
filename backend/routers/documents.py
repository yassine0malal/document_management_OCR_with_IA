from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from ..database import db_manager
from ..services.ocr import ocr_service
from ..services.classifier import classifier_service
from .auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    avis_utilisateur: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    contents = await file.read()
    # Process OCR and Classification
    text, error = ocr_service.extract_from_bytes(contents, filename=file.filename)
    if error:
        raise HTTPException(status_code=500, detail=f"OCR Error: {error}")
    
    category, confidence = classifier_service.classify(text)
    
    # Metadata extraction
    file_size = len(contents)
    content_type = file.content_type or "application/octet-stream"
    
    # Save to Database
    doc_id = db_manager.execute_query("""
        INSERT INTO Documents (id_user, nom_fichier, taille, type_mime, chemin_fichier, texte_extrait, categorie, score_confiance, avis_utilisateur)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (current_user['id_user'], file.filename, file_size, content_type, f"uploads/{file.filename}", text, category, confidence, avis_utilisateur))
    
    return {
        "id": doc_id,
        "filename": file.filename,
        "size": file_size,
        "content_type": content_type,
        "text": text,
        "category": category,
        "confidence": confidence
    }

@router.get("/")
async def list_documents(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') == 'admin':
        docs = db_manager.execute_query("SELECT * FROM Documents ORDER BY date_upload DESC")
    else:
        docs = db_manager.execute_query("SELECT * FROM Documents WHERE id_user = %s ORDER BY date_upload DESC", (current_user['id_user'],))
    return docs

@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    if current_user.get('role') == 'admin':
        stats = db_manager.execute_query("""
            SELECT categorie, COUNT(*) as count 
            FROM Documents 
            GROUP BY categorie
        """)
    else:
        stats = db_manager.execute_query("""
            SELECT categorie, COUNT(*) as count 
            FROM Documents 
            WHERE id_user = %s 
            GROUP BY categorie
        """, (current_user['id_user'],))
    return stats

@router.patch("/{doc_id}")
async def update_document(
    doc_id: int, 
    data: dict, 
    current_user: dict = Depends(get_current_user)
):
    category = data.get("categorie")
    avis = data.get("avis_utilisateur")
    
    update_fields = []
    params = []
    
    if category:
        update_fields.append("categorie = %s")
        params.append(category)
    if avis is not None:
        update_fields.append("avis_utilisateur = %s")
        params.append(avis)
        
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    params.extend([doc_id, current_user['id_user']])
    query = f"UPDATE Documents SET {', '.join(update_fields)} WHERE id_document = %s AND id_user = %s"
    
    res = db_manager.execute_query(query, tuple(params))
    if res == 0:
        raise HTTPException(status_code=404, detail="Document not found or no change made")
    
    return {"message": "Document updated successfully"}

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int, 
    current_user: dict = Depends(get_current_user)
):
    res = db_manager.execute_query(
        "DELETE FROM Documents WHERE id_document = %s AND id_user = %s",
        (doc_id, current_user['id_user'])
    )
    if res == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}
