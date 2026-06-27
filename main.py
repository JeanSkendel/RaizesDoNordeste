from fastapi import FastAPI

app = FastAPI(
    title='Projeto Raizes do Nordeste',
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