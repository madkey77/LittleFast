#PERGUNTAS
# A liquidacao deve ser parte da Antecipacao? TIpo, a antecipacao ter uma lista de OBJs Liquidacao. Ou esses conceitos tem de viver em repositorios/agregados diferentes?

class Antecipacao:
    def __init__(self, antecipacaoId, perfilId, listaUrs, valorSolicitado, spread, dataSolicitacao, status= "solicitado", totalLiquidado= 0 ) -> None:
        self.status_possiveis = ["falhou","solicitado", "confirmado", "depositado", "concluido"]
        self.id = antecipacaoId #UUID antecipacao
        self.perfilId = perfilId
        self.valorSolicitado = valorSolicitado
        self.juros = spread
        self.listaUrs = listaUrs
        self.dataSolicitacao = dataSolicitacao
        self.status = status
        self.totalLiquidado = totalLiquidado
        self.totalAverbacao = spread + valorSolicitado
    
    #Quando a averbacao for confirmada, chamar este metodo
    def confirmada(self):
            self.status = self.status_possiveis[2]

    #Quando a averbacao for depositada, chamar este metodo       
    def depositada(self):
        self.status = self.status_possiveis[3]
    
    #Caso falhe ou seja cancelada, chamar este metodo      
    def falhou(self):
        self.status = self.status_possiveis[0]

    #Atualiza o total liquidado e verifica se já foi completamente liquidada. Caso o tenha, atualiza o status para concluido
    def atualizarTotalLiquidado(self,valorLiquidado):
        self.totalLiquidado += valorLiquidado
        if self.totalLiquidado == self.totalAverbacao:
            self.status = self.status_possiveis[4]

        