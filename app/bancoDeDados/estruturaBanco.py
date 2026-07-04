import bcrypt
from sqlalchemy import Column, Integer, String, Enum as perfilEnum

from app.bancoDeDados.conexao import Base
from app.perfil.usuario import Perfil


class Usuario(Base):
    __tablename__ = "usuarios"

    idUsuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    senha = Column(String, nullable=False)
    perfil = Column(perfilEnum(Perfil), nullable=False)

    #Responsável por gerar o hash da senha
    def gerarHash(self, senha: str) -> str:
        senhaHash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        self.senha = senhaHash.decode('utf-8')

    #Verifica a senha armazenada com hash
    def verificarSenha(self, senha: str) -> bool:
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha.encode('utf-8'))