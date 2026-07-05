import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.bancoDeDados.conexao import SessionLocal
from app.bancoDeDados.estruturaBanco import Pedido, CanalPedido, StatusPedido
from app.controle.autenticarUsuario import verificarToken

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Processar pagamento do pedido
@router.post("/pagamentos/{idPedido}")
def processar_pagamento(idPedido: int, db: Session = Depends(get_db), usuario = Depends(verificarToken)):
    pedido = db.query(Pedido).filter(Pedido.idPedido == idPedido, Pedido.clienteEmail == usuario.email).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Erro: Pedido não encontrado!")

    if pedido.canalPedido == CanalPedido.caixa and usuario.perfil != "funcionario":
        raise HTTPException(status_code=403, detail="Somente funcionários podem processar pagamentos no caixa")
    elif pedido.canalPedido != CanalPedido.caixa and usuario.perfil != "cliente":
        raise HTTPException(status_code=403, detail="Somente clientes podem realizar pagamentos fora do caixa")

    #Simula a aprovação de pagamento
    pagamento = random.choice([True, False])

    #Faz a verificação se o pagamento foi ou não aprovado
    if pagamento == True:
        pedido.status = StatusPedido.pedidoEmPreparacao
        statusMensagem = "O pagamento foi aprovado! Seu pedido agora está em preparação."
    else:
        pedido.status = StatusPedido.cancelarPedido
        statusMensagem = "Atenção: Seu pagamento foi recusado! Estamos cancelando o seu pedido. :("

    db.commit()
    db.refresh(pedido)
    return {"idPedido": pedido.idPedido, "status": pedido.status, "mensagem": statusMensagem}