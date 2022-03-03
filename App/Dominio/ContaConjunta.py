class ContaConjunta:
    def __init__(self,saldoInicial, limiteAntecipacaoGlobal, listaNaoLiquidado={}, listaReservas= {}) -> None:
        self.limiteContaConjunta = saldoInicial
        self.limiteAntecipacaoGlobal = limiteAntecipacaoGlobal 
        self.listaNaoLiquidado = listaNaoLiquidado #ID antecipacao : valorSolicitado
        self.listaReservas = listaReservas # ID antecipacao : valorSolicitado
    
    #Antecipacoes criadas reservam o valor e "vivem" separadas do valor nao liquidado
    def adicionarReserva(self,valorSolicitado, antecipacaoId):
        self.reservas.update({antecipacaoId:valorSolicitado})

    #Remove um valor a partir do ID da antecipacao da lista de reservas
    def removerReserva(self,antecipacaoId):
        if antecipacaoId in self.reservas:
            self.reservas.pop(antecipacaoId)

    #Retirao valor do dict de reservas e acrescenta no de valores nao liquidados
    def novaAntecipacao(self, antecipacaoId):
        self.listaNaoLiquidado.update(antecipacaoId, self.listaReservas[antecipacaoId])
        self.removerReserva(antecipacaoId)
    
    #Retirao valor do dict valores nao liquidados (valor liquidado)
    def novaLiquidacao(self, antecipacaoId):
        self.listaNaoLiquidado.pop(antecipacaoId)

    def valorTotalNaoLiquidado(self):
        return sum(valorLiquidacao for valorLiquidacao in self.listaNaoLiquidado.values())

    def valorTotalReservado(self):
        return sum(valorReservado for valorReservado in self.listaNaoLiquidado.values())
    
    #valor total comprometido com reservas e valores nao liquidados
    def valorTotalComprometido(self):
        return self.valorTotalReservado() + self.valorTotalNaoLiquidado()
    
    def saldoDisponivel(self):
        return self.limiteContaConjunta - self.valorTotalComprometido() 

    def porcentualComprometido(self):
        return (self.limiteContaConjunta - self.valorTotalComprometido())*100/self.limiteContaConjunta
    
    #Define novo limite global de antecipacao
    def atualizarLimiteAntecipacao(self, novoLimite):
        self.limiteAntecipacaoGlobal = novoLimite
    
    # Atualiza o limite da Conta Conjunta
    def atualizarLimiteContaConjunta(self,novoLimite):
        self.limiteContaConjunta = novoLimite
    #Confere se o valor inputado está disponivel para ser antecipado
    def valorEstaDisponivelContaConjunta(self, valorSolicitado):
        saldoPosAntecipacao = valorSolicitado + self.valorTotalComprometido()
        return self._politicaAntecipacao(saldoPosAntecipacao)
        
    def _politicaAntecipacao(self, saldoPosAntecipacao):
        limiteCriticoSaldo =  self.limiteContaConjunta * 0.8 #regra que limita o valor disponivel pra antecipacao com relacao ao limite da conta
        return saldoPosAntecipacao <= limiteCriticoSaldo