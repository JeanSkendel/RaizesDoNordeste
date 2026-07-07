from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.bancoDeDados.conexao import SessionLocal
from app.bancoDeDados.estruturaBanco import LogAuditoria
from app.controle.autenticarUsuario import verificarToken
from app.erros.tratarErros import tratarErro

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Imprimete os logs de auditoria
@router.get("/logs")
def listar_logs(db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil != "gerente":
        raise tratarErro(403, "Somente o cargo de gerente pode consultar os logs de auditoria!")

    logs = db.query(LogAuditoria).order_by(LogAuditoria.timestamp.desc()).all()
    return [{"idLog": log.idLog, "idUsuario": log.idUsuario, "acao": log.acao, "detalhe": log.detalhe, "timestamp": log.timestamp } for log in logs]