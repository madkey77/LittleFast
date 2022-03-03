import sys
from LittleFast.App.Dominio.ContaConjunta import ContaConjunta

from LittleFast.App.Dominio.Recebiveis import Recebiveis
sys.path.insert(0, 'C:\Users\Matheus Sales\Desktop\Rapdin\Codigos\LittleFast\App\Dominio')

import Antecipacao
import ferramentas
import json
import ContaConjunta


class SolicitarAntecipacao:
    def __init__(self, jsonStringAntecipacao : str, jsonStringRecebiveisUsuario :str) -> None:
        
        #talvez chamar funcoes que carregam os Recebiveis e ContaConjunta da DB aqui
        paramAntecipacao = json.loads(jsonStringAntecipacao)
        paramRecebiveis = json.loads(jsonStringRecebiveisUsuario)
        paramContaConjunta = json.loads(jsonStringContaConjunta)
        self.antecipacao = Antecipacao(**paramAntecipacao)
        self.recebiveisUsuario = Recebiveis(**paramRecebiveis)
        self.contaConjunta = ContaConjunta(**paramContaConjunta)
        self.perfil = Perfil()
        #Declarar objeto do usuario

        self._atualizarSaldoUsuario()
        repositorios.antecipacao.salvarAntecipacao(self.antecipacao)

    def executar(self):
        self.contaConjunta = ContaConjunta() #Update das infos de "ContaConjunta" (NAO IMPLEMENTADO)
        self.contaConjunta.valorDisponivelContaConjunta(self.antecipacao.valorSolicitacao)
        self.contaConjunta.adicionarReserva(self.antecipacao.valorSolicitacao,self.antecipacao.id)
        repositorios.contaConjunta.atualizar(self.contaConjunta) #Chama funcao da interface que salva no DB o novo saldo disponivel
        integracaoTag.enviarAverbacao() #Chama funcao que envia solicitacao a integracao para a TAG
    
    def falhou(self):
        self.contaConjunta = ContaConjunta()  #Update das infos de "ContaConjunta" (NAO IMPLEMENTADO)
        self.contaConjunta.removerReserva(self.antecipacao.id)
        self.antecipacao.falhou() #Atualiza status antecipacao para "falhou"
        repositorios.contaConjunta.atualizar(self.contaConjunta) #Chama funcao da interface que salva no DB o novo saldo disponivel
        repositorios.antecipacao.atualizar(self.antecipacao)
    
    def confirmada(self):
        self.contaConjunta = ContaConjunta()  #Update das infos de "ContaConjunta" (NAO IMPLEMENTADO)
        self.contaConjunta.novaAntecipacao(self.antecipacao.id)
        self.antecipacao.confirmada() #Atualiza status antecipacao para "falhou"
        repositorios.depositos.depositoLiberado(self.antecipacao.valorSolicitado, self.perfil.id) #Envia para DB de depositos (notion)
        repositorios.contaConjunta.atualizar(self.contaConjunta) #Chama funcao da interface que salva no DB o novo saldo disponivel
        repositorios.antecipacao.atualizar(self.antecipacao)  
    
    def depositada(self):
        self.antecipacao.depositada() #Atualiza status antecipacao para "falhou"
        repositorios.antecipacao.atualizar(self.antecipacao) 

    def concluida(self):
        self.contaConjunta = ContaConjunta()  #Update das infos de "ContaConjunta" (NAO IMPLEMENTADO)
        self.contaConjunta.novaLiquidacao(self.antecipacao.id)
        self.antecipacao.confirmada() #Atualiza status antecipacao para "falhou"
        repositorios.contaConjunta.atualizar(self.contaConjunta) #Chama funcao da interface que salva no DB o novo saldo disponivel
        repositorios.antecipacao.atualizar(self.antecipacao)       
         
    
    def _atualizarSaldoUsuario(self):
        self.perfil.atualizarSaldoDisponivel()#ja subtrai o valor solicitado+juros do Limite Adiante
        repositorios.perfil.atualizarUsuario(self.perfil)



    def gerarID(self):
        pass

