from dataclasses import dataclass
from datetime import datetime


@dataclass
class Liquidacao:
    def __init__(self, antecipacaoId, idUR, dataEsperada : datetime, valorAverbado,foiLiquidada= False, dataLiquidacao= None, observacao= "") -> None:
        self.antecipacaoId = antecipacaoId
        self.idUR = idUR
        self.dataEsperada = dataEsperada
        self.dataLiquidacao = dataLiquidacao
        self.valorAverbado = valorAverbado
        self.foiLiquidada = foiLiquidada
        self.observacao = observacao
    
    def liquidada(self):
        self.foiLiquidada = True
        self.dataLiquidacao = datetime.today()

    def atualizarObservacao(self, mensagem : str):
        self.observacao = mensagem

    def estaAtrasada(self) -> datetime:
        return datetime.today() > self.dataEsperada
    