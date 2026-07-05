from fastapi import FastAPI

from app.bancoDeDados.conexao import Base, engine
from app.controle import autenticarUsuario, pedidos, pagamento

app = FastAPI(
    title='Raizes do Nordeste',
    description='Atividade prática',
    version='1.0'
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

app.include_router(autenticarUsuario.router)
app.include_router(pedidos.router)
app.include_router(pagamento.router)
Base.metadata.create_all(engine)