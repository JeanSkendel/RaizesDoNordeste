# Trabalho Prático Raízes do Nordeste -- API

## Descrição
Projeto criado para desenvolver uma API em Back-End para implementação de um comércio chamado Raízes do Nordeste que deseja ampliar o seu comercio. 

## Pré-Requisitos
Python versão: 3.13.7

Usar o ambiente virtual venv.

Baixar os pacotes do requirements

## Instalação
### Instalação do ambiente virtual:
```bash
python -m venv venv
```
### Ativar o ambiente virtual no Windows:
```bash
.venv\Scripts\activate
```
### Ativar o ambiente virtual no Linux:
```bash
source venv/bin/activate
```
### Baixar os pacotes do requirements
```bash
pip install -r requirements.txt
```

## Executar o projeto no terminal
uvicorn main:app --reload

Acessar a documentação pelo Swagger:

"http://localhost:8000/docs"


## Endpoins principais:
/usuario,
/pedido,
/pagamento,
/estoque,
/fidelidade
/auditoria.

## Processo de fluxo:
Usuário acessa a página, faz cadastro e realiza o login.

Cliente acessa a função /criarPedidos, é informado o Canal do pedido (app, web, totem). Funcionário acessa somente o caixa.

Cliente acessa /processarPagamento e efetua o pagamento (pagamento mock)

Gerente ou funcionário /atualizarStatusPedido do pedido.

Cliente aceita o /consentimentoLGPD e recebe pontos por pedido entregue.

Cliente acessa /fidelidade e consulta os pontos de fidelidade.

Cliente acessa /resgatar e resgata os pontos de fidelidade.