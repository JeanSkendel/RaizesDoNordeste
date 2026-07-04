from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.bancoDeDados.conexao import SessionLocal
from app.bancoDeDados.estruturaBanco import CanalPedido, StatusPedido, Pedido, PedidoItem
from app.controle.autenticarUsuario import verificarToken

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Criar pedidos
@router.post("/pedidos")
def criar_pedidos(itens: list[dict],canalPedido: CanalPedido, db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil == "cliente" and canalPedido == CanalPedido.caixa:
        raise HTTPException(status_code=403, detail="Clientes não podem criar pedidos no canal caixa")
    if usuario.perfil == "funcionario" and canalPedido != CanalPedido.caixa:
        raise HTTPException(status_code=403, detail="Funcionários só podem criar pedidos no canal caixa")
    if usuario.perfil not in ["cliente", "funcionario"]:
        raise HTTPException(status_code=403, detail="Somente clientes ou funcionários podem criar pedidos")

    pedido = Pedido(clienteEmail=usuario.email, canalPedido=canalPedido, idUsuario=usuario.idUsuario, status=StatusPedido.aguardarPagamento)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    estoque = 1
    for item in itens:
        produto_id = item.get("idProduto", 1)
        quantidade = item.get("quantidade", 1)

    #Verificar estoque
    if not estoque or estoque <= 0:
        raise HTTPException(status_code=400, detail=f"Produto {produto_id} sem estoque disponível")

    estoque -= quantidade
    if estoque < 0:
        raise HTTPException(status_code=400, detail="Saldo de estoque insuficiente")
    pedidosItem = PedidoItem(idPedido=pedido.idPedido, idProduto=produto_id, quantidade=estoque)
    db.add(pedidosItem)
    db.commit()
    db.refresh(pedido)
    return {"idPedido": pedido.idPedido, "canalPedido": pedido.canalPedido, "status": pedido.status, "itens": [{"idProduto": i.idProduto, "quantidade": i.quantidade} for i in pedido.itens]}

#Permite o funcionário e o gerente listar os pedidos criados
@router.get("/pedidos")
def listar_pedidos(db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil in ["funcionario", "gerente"]:
        return db.query(Pedido).all()
    return db.query(Pedido).filter(Pedido.clienteEmail == usuario.email).all()

#Permite o funcionário e o gerente atualizar os status dos pedidos
@router.patch("/pedidos/{idPedido}")
def atualizar_status(idPedido: int, atualizaStatus: StatusPedido, db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil not in ["funcionario", "gerente"]:
        raise HTTPException(status_code=403, detail="Somente funcionários ou gerentes podem atualizar pedidos")

    pedido = db.query(Pedido).filter(Pedido.idPedido == idPedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    pedido.status = atualizaStatus
    db.commit()
    db.refresh(pedido)
    return {"idPedido": pedido.idPedido, "status": pedido.status}
