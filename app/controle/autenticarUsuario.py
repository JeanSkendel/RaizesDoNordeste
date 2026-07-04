import datetime
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Form
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.bancoDeDados.conexao import SessionLocal
from app.bancoDeDados.estruturaBanco import Usuario, Perfil

router = APIRouter()

SECRET_KEY = "bf1347g49t89c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Criar Token do usuário
def criarTokenUsuario(data: dict, dataExpiracao: timedelta = None):
    dadosToken = data.copy()
    expirarToken = datetime.now(timezone.utc) + (dataExpiracao or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    dadosToken.update({"exp": expirarToken})
    return jwt.encode(dadosToken, SECRET_KEY, algorithm=ALGORITHM)

#Verificar senha
def verificarSenha(token: str = Depends(oauth2_scheme)):
    try:
        dadosToken = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = dadosToken.get("tokenUsuario")
        if email is None:
            raise HTTPException(status_code=401, detail="Atenção: Esse Token é inválido!")
    except JWTError:
        raise HTTPException(status_code=401, detail="Atenção: Este Token parece inválido ou expirado!")

#Cadastrar usuário
@router.post("/cadastroUsuario")
def cadastrar_usuario(nome: str, telefone: str, email: str, senha: str, perfil: Perfil, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise HTTPException(status_code=400, detail="Erro: Este e-mail já está sendo usado por outro usuário!")

    usuario = Usuario(nome=nome, telefone=telefone, email=email, perfil=perfil)
    usuario.gerarHash(senha)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return {"idUsuario": usuario.idUsuario, "nome": usuario.nome, "telefone": usuario.telefone, "email": usuario.email, "perfil": usuario.perfil}

#Entrar na conta do usuário
@router.post("/entrar")
def entrar(usuarname: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == usuarname).first()
    if not usuario or not usuario.verificarSenha(password):
        raise HTTPException(status_code=401,detail="Erro: Os dados informados são inválidos!")
    token = criarTokenUsuario({"tokenUsuario": usuario.email, "perfil": usuario.perfil})
    return {"access_token": token, "token_type": "bearer"}
