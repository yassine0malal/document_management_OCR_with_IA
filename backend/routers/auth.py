from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..auth import verify_password, create_access_token, decode_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from ..database import db_manager
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db_manager.execute_query("SELECT * FROM Utilisateurs WHERE email = %s", (payload['sub'],))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user[0]

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db_manager.execute_query("SELECT * FROM Utilisateurs WHERE email = %s", (form_data.username,))
    if not user or not verify_password(form_data.password, user[0]['mot_de_passe_hash']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(
        data={"sub": user[0]['email']}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user[0]}

@router.post("/register")
async def register(data: dict):
    nom = data.get("nom")
    email = data.get("email")
    password = data.get("password")
    
    if not nom or not email or not password:
        raise HTTPException(status_code=400, detail="Tous les champs sont obligatoires")
    
    # Check if user already exists
    existing_user = db_manager.execute_query("SELECT * FROM Utilisateurs WHERE email = %s", (email,))
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà")
    
    # Hash password and save
    hashed_pwd = get_password_hash(password)
    db_manager.execute_query(
        "INSERT INTO Utilisateurs (nom, email, mot_de_passe_hash) VALUES (%s, %s, %s)",
        (nom, email, hashed_pwd)
    )
    
    return {"message": "Compte créé avec succès"}

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
