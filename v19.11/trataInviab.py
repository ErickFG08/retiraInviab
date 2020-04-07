# -*- coding: latin-1 -*-

class cRegras():

    """
    classe responsavel a armazenara as regras de flexibilizacao

    variaveis:
        listaTipoRestr          List        Lista contendo o tipo das restricoes
        listaCodRestr           List        Lista contendo o codigo das restricoes
        listaEtapaRestr         List        Lista contendo a etapa da restricao
        listaIteracao           List        Lista contendo a partir de qual etapa a restricao sera flexibilizada
        listaLimite             List        Lista contendo a informacao se eh limite superior (1) ou inferior (0)
        listaTipoRestrFlex      List        Lista contendo o tipo da restricao de que deve ser flexibilizada
        listaCodRestrFlex       List        Lista contendo o codigo  da restricao que deve ser flexibilizada
        listaLimiteFlex         List        Lista contendo a informacoo se eh para retirar do limite superior (1) ou inferior (0)
        listaUsinaEnvolvida     List        Lista contendo o codigo da usina cuja restricao deve ser flexibilizada

    funcoes:
        carregaRegraInviab      verifica se o arquivo regrainviab.txt existe e le as regras de flexibilizacao
    """
    def __init__(self):
        # inicializa as listas
        self.listaTipoRestr = []
        self.listaCodRestr = []
        self.listaEtapaRestr = []
        self.listaIteracao = []
        self.listaLimite = []
        self.listaTipoRestrFlex = []
        self.listaCodRestrFlex = []
        self.listaLimiteFlex = []
        self.listaUsinaEnvolvida = []

    #funcao que carrega as regras de inviabilidades
    def carregaRegraInviab(self):

        valida = True

        # abre o arquivo de log, para informar o andamento do processo de leitura das regras de flexibilizacao
        with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
            # informa que esta na etapa de leitura das regras
            arqRetInviab.write('\nINICIO DA ETAPA DE LEITURA DAS REGRAS DE FLEXIBILIZACAO\n')
        try:
            # tenta abrir o arquiv
            with open('regrainviab.txt', 'r', encoding="latin_1") as arqRegraInviab:
                # pula 3 linhas
                for i in range(3): arqRegraInviab.readline()
                # varre o arquivo
                iregras = 0
                for linha in arqRegraInviab:
                    iregras += 1
                    # atualiza a lista
                    self.listaTipoRestr.append(linha[1:3].strip())
                    self.listaCodRestr.append(int(linha[5:8]))
                    self.listaEtapaRestr.append(int(linha[11:13]))
                    self.listaIteracao.append(int(linha[15:17]))
                    self.listaLimite.append(int(linha[19:20]))
                    self.listaTipoRestrFlex.append(linha[23:25].strip())
                    self.listaCodRestrFlex.append(int(linha[27:30]))
                    self.listaLimiteFlex.append(int(linha[32:33]))
                    self.listaUsinaEnvolvida.append((linha[35:38]).strip())

                # abre o arquivo de log, para informar informa quantas regras foram lidas
                with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
                    arqRetInviab.write('Foram lidas ' + str(iregras) + ' regras de flexibilizacao\n')

        # se nao consegui eh por que ele nao existe
        except IOError:
            #se nao achou o arquivo, imprime no log e sai da rotina
            print('arquivo regrainviab.txt nao encontrado')
            # escreve no arquivo de Log que nao encontrou o arquivo
            with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
                arqRetInviab.write('ERRO: arquivo de tratamento das inviabilidades regrainviab.txt nao encontrado, o processo sera interrompido\n')
            valida = False

        return valida
