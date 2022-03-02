# Ignorei todas as verificações de usuario por entender que nao importa neste nivel da abstracao
# Fiz sem pensar muito na forma da persistência (algumas partes podem requerer adaptacao caso existam copias das URs e afins, mas imagino que ja tem um jeito de lidar com isso)
# Foquei em modelar de forma parecida com o dominio e lembrando das formas de acessar os dados de forma simples

# PERGUNTAS
# 1. O jeito qeu utilizei pra manipular e acessar as infos das classes de baixo ta certo? Ou tenho que criar um objeto para tipo: x = UR(novaUr); x.metodoDePagamento quando for acessar as URs de uma lista de URs (agenda) por ex
# 2. Se a pergunta acima for verdadeira, o ideal seria que os __init__ recebecem um json quem nem na classe UR (pensando na hora que for recriar os objetos do DB), não deixar nenhum valor HardCoded (apenas configurar com opcional e um  "default"?)
# 3. Deveria separar essas classes em arquivos diferentes?

from dataclasses import dataclass
import datetime
from datetime import date, timedelta
from types import SimpleNamespace
import json


import datetime
from typing import List
from uuid import UUID

# talvez separar essas Ferramentas em arquivo separado
# Carrega o objeto json e transforma em objetos dentro da classe UR (basicamente converte o Json em um objeto)
def jsonToObject(jsonString):
    return json.loads(jsonString, object_hook=lambda d: SimpleNamespace(**d))

# Converte a data no json em um objeto datetime
def stringToDate(dataString):
    data = dataString[:18]  # Corta parte com .z54 (ou algo do tipo)
    return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S')


class UR:
    def __init__(self, jsonStringUR) -> None:

        # Pensei em fazer assim porque consigo criar um contexto de acesso mais focado no dominio sem deixar pra trás
        # nenhuma info que outros servicos low level possam precisar no backend
        self.data = jsonToObject(jsonStringUR)

        # Parseamento de algumas infos cruciais no objeto para fácil acesso
        self.id = self.data.settlementExpectations.key  # ID da UR
        # Bandeira do cartao composta por 3 letas (ex."VCC", "MCC") -> (Visa , Mastercard)
        self.metodoDePagamento = self.data.settlementExpectations.paymentScheme
        # Expectativa de liquidacao da UR
        self.expectativaDeLiquidacao = self.data.settlementExpectations.expectedSettlementDate
        self.valorTotal = self.data.settlementExpectations.totalAmount  # Valor Total da UR
        # Verificar em https://docs.taginfraestrutura.com.br/reference/posicao-de-agenda-titular. Parece que chaparam no exemplo e colocaram "200" ai inves de "100" em "committedAmount"
        self.valorComprometido = self.data.settlementExpectations.committedAmount
        self.valorDisponivel = self.data.settlementExpectations.uncommittedAmount
        # trocar talvez pra self.credenciador?
        self.pagador = self.data.settlementExpectations.debtor
        self.ultimaAtualizacao = stringToDate(
            self.data.settlementExpectations.lastUpdated)

    def atualizarUR(self, jsonStringNovaUR, urId):
        novaUR = UR(jsonStringNovaUR)
        if self.podeAtualizar(novaUR.id, novaUR.ultimaAtualizacao):
            # Aqui podemos definir se vamos substituir todas as infos da UR ou só permitir a atualização (acrescentar infos e recalcular outras)
            pass

    def podeAtualizar(self, novaUR_IdUnico, novaUR_ultimaAtualizacao) -> bool:
        return self.id == novaUR_IdUnico and self.ultimaAtualizacao < novaUR_ultimaAtualizacao

#Conjunto de URs agrupadas por metodo de pagamento
class Agenda:
    def __init__(self, agendaId, marketplaceId: str, metodoDePagamento: str, URs: List[UR], calendarioURs= {}) -> None:
        # VER DOCUMENTACAO TAG PARA CRIAR OBJETO
        self.id = agendaId  # Novo UUID para agenda *****
        self.marketplaceId = marketplaceId
        # bandeira do cartao (por hora)
        self.metodoDePagamento = metodoDePagamento
        # Criar novo OBJ UR ou por ter passado List[UR] em __init__ ele ja esta esperando esse tipo de obj?
        self.URs = {self.adicionarNovaUR(UR(novaUR)) for novaUR in URs}
        self.calendarioURs = calendarioURs

    def adicionarNovaUR(self, novaUR):
        # Fazer verificacao se realmente pode adicionar essa UR a essa agenda
        # Mapeia lista de URs por ID da UR.
        self.URs[novaUR.id] = novaUR
        # Mapeia data de liquidacao ->  id da UR da UR.
        self.calendarioURs[novaUR.expectativaDeLiquidacao] = novaUR.id

    # Faz o somatorio do saldo nao comprometido das URs registradas nesta agenda
    def saldoDisponivel(self):
        # nao sei se é realmente um inteiro esse valor (imagino que nao), mas nao consegui entender como a resposta da api retorna valores fracionados. Se for o caso, atualizar metodos que calculam saldo
        saldoDisponivelTotal = sum(int(atualUR.valorDisponivel)
                                   for atualUR in self.URs)
        return saldoDisponivelTotal

    # Organiza as URs de acordo com a data de liquidacao
    def organizarURs(self):
        self.URs.sort(key=lambda atualUR: atualUR.expectativaDeLiquidacao)
        self.calendarioURs.sort(self.calendarioURs.keys())

    # Volta lista de IDs das URs que vencem na data inserida
    def filtroPorData(self, data):
        somaURsEsperadas = 0
        for unidadeRecebivel in self.calendarioURs.keys():
            if (data == unidadeRecebivel):
                idEsperado = self.calendarioURs[unidadeRecebivel]
                valorDisponivel = self.URs[idEsperado].valorDisponivel
                saldoPorId = {idEsperado: valorDisponivel}
                somaURsEsperadas += valorDisponivel
        return {'saldo_esperado': somaURsEsperadas, 'saldo_por_id': saldoPorId}

# Conjunto de agendas por marketplace
class ColecaoAgendasMarketplace:
    def __init__(self, perfilId, marketplaceId, agendas= {}) -> None:
        self.perfilId = perfilId
        self.marketplaceID = marketplaceId
        self.agendas = agendas

    # Politica para add nova agenda
    def podeAdicionarAgenda(self, novaAgenda: Agenda) -> bool:
        # Compara se nao esta adicionando uma agenda de uma bandeira de cartao ja adicionada
        return novaAgenda.metodoDePagamento not in self.agendas

    def adicionarAgenda(self, novaAgenda: Agenda):
        if self.podeAdicionarAgenda(novaAgenda):
            # Mapeia agendas por meio de pagamento (Bandeira cartao)
            self.agendas[novaAgenda.metodoDePagamento] = novaAgenda

    def saldoDisponivel(self):
        saldoTotalDisponivelMarketplace = sum(
            i.saldoDisponivel for i in self.agendas.values())
        return saldoTotalDisponivelMarketplace

# Conjunto de todos os recebiveis de um usuario (talvez nao seja necessario agora ja que so vamos lidar com uma colecao por vez mas pensei em ja fazer assim para quando formos lidar com mais de 1 ao mesmo tempo)
class Recebiveis():
    def __init__(self, perfilId, colecoes= {}, ultimaAtualizacao= datetime.today()) -> None:
        self.perfilId = perfilId
        self.colecoes = colecoes
        self.ultimaAtualizacao= ultimaAtualizacao  # pode ser desnecessario isso

    def adicionarColecao(self, novaColecao: ColecaoAgendasMarketplace) -> None:
        if self.podeAdicionarColecao(self, novaColecao):
            self.colecoes[novaColecao.marketplaceID] = novaColecao

    def podeAdicionarColecao(self, novaColecao: ColecaoAgendasMarketplace):
        return novaColecao.marketplaceId not in self.colecoes.keys()

    def saldoDisponivel(self):
        return sum(i.saldoDisponivel for i in self.colecoes.values())

    # Retorna o saldo esperado para a data inserida e os IDs das URs que tem prazo de liquidacao esperado para essa data
    def saldoEsperadoNoDia(self, dataEsperada, marketplaceId):
        saldoEsperado = 0
        idsURsEncontrados = []
        for agenda in self.colecoes[marketplaceId]:
            for unidadeRecebivel in agenda.calendarioURs.values():
                filtrado = unidadeRecebivel.filtroPorData(dataEsperada)
                idsURsEncontrados.append(filtrado['saldo_por_id'].keys())
                saldoEsperado += filtrado['saldo_esperado']
        return {'saldo_na_data': saldoEsperado, 'ids_urs_encontrados': idsURsEncontrados}

    # temos de antecipar URs com 30 dias ou menos p/ liquidacao porque é o mínimo que combinamos com a adiante (2,8%/mes) e imagino que nao teremos juros variavel por hora
    def alocarValorAntecipacao(self, valorSolicitado, marketplaceId):
        valorAlocado = 0
        ursAlocadas = {}
        ultima_data = date.today()
        # talvez essa logica de limitar a 30 dias deva ser aplicada antes de exibir as infos pro usuario
        dataInterador = ultima_data + datetime.timedelta(days=30)
        # Busca data da UR com vencimento mais distante naquele marketplace
        for agenda in self.colecoes[marketplaceId]:
            agenda.organizarURs()
            dataUR = agenda.calendarioURs[-1]  # pega a data mais distante
            if ultima_data < dataUR:
                ultima_data = dataUR
        if ultima_data > dataInterador:  # Se ultrapassar 30 dias, vamos comecar a olhar a partir de 30 dias do dia atual
            ultima_data = dataInterador
        # Buscando URs mais distantes que somadas sejam maior que o valorSolicitado (fica para a função da averbacao decidir qual vai ser a parcial)
        # Falta implementar logica para nao escolher URs que ja tenham algum tipo de averbacao (precisamos descobrir se nao há averbaçoes q os proprios mktplaces fazem por conta do sistema deles)
        while valorAlocado < valorSolicitado and dataInterador > date.today():
            saldoNoDia += self.saldoEsperadoNoDia(dataInterador)
            valorAlocado += saldoNoDia['saldo_esperado']
            ursAlocadas.update(saldoNoDia['saldo_por_id'])
            # Se as URs forem registradas para vencer apenas em dias de semana, vale a pena pular os dias não úteis
            dataInterador = dataInterador - timedelta(days=1)
        return {'valor_alocado': valorAlocado, 'urs_alocadas': ursAlocadas}
