from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.bancoDeDados.conexao import SessionLocal
from app.bancoDeDados.estruturaBanco import CanalPedido, StatusPedido, Pedido, PedidoItem, Estoque, LogAuditoria, \
    Fidelidade
from app.controle.autenticarUsuario import verificarToken
from app.erros.tratarErros import tratarErro

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Criar pedidos
@router.post("/criarPedidos")
def criar_pedidos(idProduto: int, idFilial: int, quantidade: int, canalPedido: CanalPedido, db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil == "cliente" and canalPedido == CanalPedido.caixa:
        raise tratarErro(403, "Clientes não podem criar pedidos no caixa")
    if usuario.perfil == "funcionario" and canalPedido != CanalPedido.caixa:
        raise tratarErro(403, "Funcionários só podem criar pedidos no caixa")
    if usuario.perfil not in ["cliente", "funcionario"]:
        raise tratarErro(403, "Somente clientes ou funcionários podem criar pedidos")

    pedido = Pedido(clienteEmail=usuario.email, canalPedido=canalPedido, idUsuario=usuario.idUsuario, status=StatusPedido.aguardarPagamento)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    #Verificar estoque
    estoque = db.query(Estoque).filter(Estoque.idProduto == idProduto, Estoque.idFilial == idFilial).first()
    if not estoque or estoque.quantidade <= 0:
        raise tratarErro(400, f"Atenção: Produto {idProduto} sem estoque ou indisponível!")

    estoque.quantidade -= quantidade
    if estoque.quantidade < 0:
        raise tratarErro(400, "O saldo do estoque é insuficiente!")
    pedidosItem = PedidoItem(idPedido=pedido.idPedido, idProduto=idProduto, quantidade=quantidade)
    db.add(pedidosItem)

    #Registra na auditoria a criação do pedido
    log = LogAuditoria(idUsuario=usuario.idUsuario, acao="CRIAR_PEDIDO", detalhe=f"Produto {idProduto} na filial {idFilial} atualizado para {estoque.quantidade} unidades.")
    db.add(log)
    db.commit()
    db.refresh(pedido)

    return {"idPedido": pedido.idPedido, "canalPedido": pedido.canalPedido, "status": pedido.status, "quantidade": quantidade, "Quantidade ainda disponível no estoque": [{"quantidade": i.quantidade} for i in pedido.itens]}

#Permite o funcionário e o gerente listar os pedidos criados
@router.get("/listarPedidos")
def listar_pedidos(db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil in ["funcionario", "gerente"]:
        return db.query(Pedido).all()
    return db.query(Pedido).filter(Pedido.clienteEmail == usuario.email).all()

#Permite o funcionário e o gerente atualizar os status dos pedidos
@router.patch("/atualizarStatusPedido")
def atualizar_status(idPedido: int, atualizaStatus: StatusPedido, db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    if usuario.perfil not in ["funcionario", "gerente"]:
        raise tratarErro(403, "Somente funcionários ou gerentes podem atualizar pedidos.")

    pedido = db.query(Pedido).filter(Pedido.idPedido == idPedido).first()
    if not pedido:
        raise tratarErro(404, "Erro: Pedido não encontrado!")

    pedido.status = atualizaStatus
    db.commit()
    db.refresh(pedido)

    #Após o pedido ser entregue o cliente recebe pontos de fidelidade
    if atualizaStatus == StatusPedido.pedidoEntregue:
        fidelidade = db.query(Fidelidade).filter(Fidelidade.idUsuario == pedido.idUsuario).first()
        if not fidelidade:
            fidelidade = Fidelidade(idUsuario=pedido.idUsuario, pontos=0)
            db.add(fidelidade)

        logFidelidade = db.query(LogAuditoria).filter(LogAuditoria.idUsuario == pedido.idUsuario, LogAuditoria.acao == "FIDELIDADE", LogAuditoria.detalhe.like(f"%Pedido {pedido.idPedido}%")).first()

        if not logFidelidade:
            pontos = sum(item.quantidade for item in pedido.itens)
            fidelidade.pontos += pontos

            log = LogAuditoria(idUsuario=pedido.idUsuario, acao="FIDELIDADE", detalhe=f"Pedido {pedido.idPedido} entregue. Cliente {pedido.clienteEmail} recebeu {pontos} ponto(s) de fidelidade!")
            db.add(log)

        db.commit()
        db.refresh(fidelidade)

    return {"idPedido": pedido.idPedido, "status": pedido.status}