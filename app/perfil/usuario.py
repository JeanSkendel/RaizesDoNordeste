from enum import Enum
import bcrypt

#Armazena a seleção do perfil do usuário
class Perfil(str, Enum):
    cliente = 'cliente'
    funcionario = 'funcionario'
    gerente = 'gerente'

#Cria a classe usuário
class Usuario:
    def __init__(self, nome: str, telefone: str, email: str, senha: str, perfil: Perfil):
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.senha = senha
        self.perfil = perfil

    #Responsável por gerar o hash da senha
    def gerarHash(self, senha: str) -> str:
        senhaHash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        return senhaHash.decode('utf-8')

    #Verifica a senha armazenada com hash
    def verificarSenha(self, senha: str) -> bool:
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha.encode('utf-8'))