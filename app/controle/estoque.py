from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.bancoDeDados.conexao import SessionLocal
from app.bancoDeDados.estruturaBanco import Estoque, LogAuditoria
from app.controle.autenticarUsuario import verificarToken
from app.erros.tratarErros import tratarErro

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Permite o gerente atualizar o estoque
@router.post("/atualizarEstoque")
def atualizar_estoque(idProduto: int, idFilial: int, quantidade: int, db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil not in ["gerente"]:
        raise tratarErro(403,"Erro: Somente o gerente pode movimentar o controle!")

    estoque = db.query(Estoque).filter(Estoque.idProduto == idProduto, Estoque.idFilial == idFilial).first()
    if not estoque:
        estoque = Estoque(idProduto=idProduto, idFilial=idFilial, quantidade=0)
        db.add(estoque)

    estoque.quantidade += quantidade
    if estoque.quantidade < 0:
        raise tratarErro(400,"Atenção: Saldo insuficiente para saída")

    db.commit()
    db.refresh(estoque)

    #Registra a atualização de estoque na auditoria
    log = LogAuditoria(usuario.idUsuario, acao="atualizarEstoque", detalhe=f"Produto {idProduto} na filial {idFilial} e quantidade {quantidade} unidades.")
    db.add(log)
    db.commit()
    return {"idProduto": estoque.idProduto, "idFilial": estoque.idFilial, "quantidade": estoque.quantidade}

#Permite o funcionário ou gerente consultar o estoque
@router.get("/consultarEstoque")
def consultar_estoque(idFilial: int, db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil not in ["funcionario", "gerente"]:
        raise tratarErro(403,"Somente funcionários ou gerentes podem consultar controle")

    estoque = db.query(Estoque).filter(Estoque.idFilial == idFilial).all()
    return [{"idProduto": e.idProduto, "quantidade": e.quantidade} for e in estoque]