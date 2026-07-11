from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.bancoDeDados.conexao import SessionLocal
from app.bancoDeDados.estruturaBanco import Fidelidade, LogAuditoria, Usuario
from app.controle.autenticarUsuario import verificarToken
from app.erros.tratarErros import tratarErro

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Permite consultar os pontos de fidelidade
@router.get("/consultarPontos")
def consultar_pontos_cliente(db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil != "cliente":
        raise tratarErro(403, "Somente clientes possuem programa de fidelidade")
    if not usuario.consentimentoLGPD:
        raise tratarErro(403, "Atenção: É nessário aceitar o consentimento LGPD para usar o programa de fidelidade!")

    fidelidade = db.query(Fidelidade).filter(Fidelidade.idUsuario == usuario.idUsuario).first()
    if not fidelidade:
        fidelidade = Fidelidade(idUsuario=usuario.idUsuario, pontos=fidelidade.pontos)
        db.add(fidelidade)
        db.commit()
        db.refresh(fidelidade)

    return {"idUsuario": usuario.idUsuario, "pontos": fidelidade.pontos}

#Cliente precisa aceitar o consentimento de LGPD
@router.get("/consentimentoLGPD")
def consentimentoLGPD(db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    usuario = db.query(Usuario).filter(Usuario.idUsuario == usuario.idUsuario).first()
    usuario.consentimentoLGPD = True
    db.commit()
    db.refresh(usuario)

    #Após ser aceito o consentimento é registrado na auditoria
    log = LogAuditoria(
        idUsuario=usuario.idUsuario,
        acao="CONSENTIMENTO_LGPD",
        detalhe=f"Usuário {usuario.nome}, email {usuario.email} aceitou o consentimento LGPD!")
    db.add(log)
    db.commit()

    return {"mensagem": "O consentimento do usuário foi registrado com sucesso!"}

#Permite o cliente resgatar os pontos de fidelidade
@router.get("/resgatar")
def resgatar_pontos_fidelidade(resgatarPontos: int, db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil != "cliente":
        raise tratarErro(403, "Somente clientes podem resgatar os pontos de fidelidade!")
    if not usuario.consentimentoLGPD:
        raise tratarErro(403, "Atenção: É necessário aceitar o consentimento LGPD para usar o programa de fidelidade!")

    fidelidade = db.query(Fidelidade).filter(Fidelidade.idUsuario == usuario.idUsuario).first()
    if not fidelidade or fidelidade.pontos < resgatarPontos:
        raise tratarErro(400, "Aviso: Os pontos para resgate são insuficientes!")

    fidelidade.pontos -= resgatarPontos
    db.commit()
    db.refresh(fidelidade)

    return {"idUsuario": usuario.idUsuario, "pontosRestantes": fidelidade.pontos, "mensagem": "O resgate dos pontos foi realizado com sucesso!"}