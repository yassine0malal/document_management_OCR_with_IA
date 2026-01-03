from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List

from .auth import verify_password, create_access_token, decode_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from .database import db_manager
from .services.ocr import ocr_service
from .services.classifier import classifier_service

app = FastAPI(title="IntelliDoc API")

# CORS setup for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db_manager.execute_query("SELECT * FROM Utilisateurs WHERE email = %s", (payload['sub'],))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user[0]

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db_manager.execute_query("SELECT * FROM Utilisateurs WHERE email = %s", (form_data.username,))
    if not user or not verify_password(form_data.password, user[0]['mot_de_passe_hash']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(
        data={"sub": user[0]['email']}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user[0]}

@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/documents/upload")
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

@app.get("/documents")
async def list_documents(current_user: dict = Depends(get_current_user)):
    docs = db_manager.execute_query("SELECT * FROM Documents WHERE id_user = %s ORDER BY date_upload DESC", (current_user['id_user'],))
    return docs

@app.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    stats = db_manager.execute_query("""
        SELECT categorie, COUNT(*) as count 
        FROM Documents 
        WHERE id_user = %s 
        GROUP BY categorie
    """, (current_user['id_user'],))
    return stats
