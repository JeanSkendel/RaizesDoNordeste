from fastapi import FastAPI

from app.bancoDeDados.conexao import Base, engine
from app.controle import autenticarUsuario, pedidos, pagamento, estoque, auditoria
from app.perfil import fidelidade

app = FastAPI(
    title='Raizes do Nordeste',
    description='Atividade prática',
    version='1.5'
)

@app.get('/')
def index():
    return {'Sistema': 'Raízes do Nordeste',
        'Usuarios': {
        'usuarios': '/cadastro',
        'usuarios': '/login'
        },
        'Pedidos': {
        'pedidos': 'criarPedidos',
        'pedidos': 'listarPedidos',
        'pedidos': 'atualizarStatusPedido'
        },
        'Pagamentos': {
        'pagamentos': 'processarPagamento'
        },
        'Estoque': {
        'estoque': 'atualizarEstoque',
        'estoque': 'consultarEstoque'
        },
        'Fidelidade': {
        'fidelidade': 'consultarPontos',
        'fidelidade': 'resgatarPontos'
        }
    }

app.include_router(autenticarUsuario.router, prefix="/usuario", tags=["Usuário"])
app.include_router(pedidos.router, prefix="/pedido", tags=["Pedido"])
app.include_router(pagamento.router, prefix="/pagamento", tags=["Pagamento"])
app.include_router(estoque.router, prefix="/estoque", tags=["Estoque"])
app.include_router(fidelidade.router, prefix="/fidelidade", tags=["Fidelidade"])
app.include_router(auditoria.router, prefix="/auditoria", tags=["Auditoria"])
Base.metadata.create_all(engine)