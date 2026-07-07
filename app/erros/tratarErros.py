from fastapi import HTTPException

#Retorna a resposta de erro
def tratarErro(codigoDeErro: int, mensagem: str):
    return HTTPException( status_code=codigoDeErro, detail={"Erro:": {"código de erro:": codigoDeErro, "mensagem": mensagem}})