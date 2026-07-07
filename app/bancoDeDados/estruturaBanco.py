from datetime import datetime, timezone
from enum import Enum

import bcrypt
from sqlalchemy import Column, Integer, String, Enum as prfEnum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.bancoDeDados.conexao import Base
from app.perfil.usuario import Perfil


class Usuario(Base):
    __tablename__ = "usuarios"

    idUsuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    senha = Column(String, nullable=False)
    perfil = Column(prfEnum(Perfil), nullable=False)
    consentimentoLGPD = Column(Boolean, nullable=False, default=False)

    #Responsável por gerar o hash da senha
    def gerarHash(self, senha: str) -> str:
        senhaHash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        self.senha = senhaHash.decode('utf-8')

    #Verifica a senha armazenada com hash
    def verificarSenha(self, senha: str) -> bool:
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha.encode('utf-8'))

class CanalPedido(str, Enum):
    app = "app"
    web = "web"
    totem = "totem"
    caixa = "caixa"

class StatusPedido(str, Enum):
    aguardarPagamento = "AguardandoConfirmacaoPagamento"
    pedidoEmPreparacao = "PedidoEmPreparacao"
    pedidoPronto = "PedidoPronto"
    pedidoEntregue = "PedidoEntregue"
    cancelarPedido = "PedidoCancelado"

class Pedido(Base):
    __tablename__ = "pedidos"

    idPedido = Column(Integer, primary_key=True, index=True)
    clienteEmail = Column(String, nullable=False)
    canalPedido = Column(prfEnum(CanalPedido), nullable=False)
    status = Column(prfEnum(StatusPedido), default=StatusPedido.aguardarPagamento)
    idUsuario = Column(Integer, ForeignKey("usuarios.idUsuario"))

    usuario = relationship("Usuario")
    itens = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")

class Produto(Base):
    __tablename__ = "produtos"

    idProduto = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)

class PedidoItem(Base):
    __tablename__ = "pedido_itens"

    idItem = Column(Integer, primary_key=True, index=True)
    idPedido = Column(Integer, ForeignKey("pedidos.idPedido"))
    idProduto = Column(Integer, ForeignKey("produtos.idProduto"))
    quantidade = Column(Integer, default=1)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")

class Estoque(Base):
    __tablename__ = "controle"

    idEstoque = Column(Integer, primary_key=True, index=True)
    idProduto = Column(Integer, ForeignKey("produtos.idProduto"))
    idFilial = Column(Integer, nullable=False)
    quantidade = Column(Integer, default=0)

    produto = relationship("Produto")

class Fidelidade(Base):
    __tablename__ = "fidelidade"

    idFidelidade = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("usuarios.idUsuario"))
    pontos = Column(Integer, default=0)

    usuario = relationship("Usuario")

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    idLog = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("usuarios.idUsuario"), nullable=True)
    acao = Column(String, nullable=False)
    detalhe = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    usuario = relationship("Usuario")

    def __init__(self, idUsuario=None, acao=None, detalhe=None):
        self.idUsuario = idUsuario
        self.acao = acao
        self.detalhe = detalhe