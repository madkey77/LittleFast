class ContaConjunta:
    def __init__(self,saldoInicial, limiteAntecipacaoGlobal, valorTotalNaoLiquidado) -> None:
        self.limiteContaConjunta = saldoInicial
        self.limiteAntecipacaoGlobal = limiteAntecipacaoGlobal
        self.valorTotalNaoLiquidado = valorTotalNaoLiquidado

    def novaLiquidacao(self, valorNovaLiquidacao):
        self.valorTotalNaoLiquidado -= valorNovaLiquidacao
    
    def novaAntecipacao(self, valorNovaAntecipacao):
        self.valorTotalNaoLiquidado += valorNovaAntecipacao
    
    def saldoDisponivel(self):
        return self.limiteContaConjunta - self.valorTotalNaoLiquidado

    def porcentualComprometido(self):
        return (self.limiteContaConjunta - self.valorTotalNaoLiquidado)*100/self.limiteContaConjunta
    
    def atualizarLimiteAntecipacao(self, novoLimite):
        self.limiteAntecipacaoGlobal = novoLimite