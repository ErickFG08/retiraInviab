# -*- coding: latin-1 -*-

import glob

class cInviab():

    """
    classe responsavel por armazenar as inviabilidades

    variaveis:
        listaTipo               List        Lista contendo o tipo da inviabilidade
        listaCod                List        Lista contendo o codigo da inviabilidade
        listaEtapa              List        Lista contendo a etapa da inviabilidade
        listaCenario            List        Lista contendo o cenario da inviabilidade
        listaLimite             List        Lista contendo a informacao se eh limite superior (1) ou inferior (0)
        listaPatamar            List        Lista contendo o patamar da inviabilidade
        listaValor              List        Lista contendo o valor da inviabilidade
        listaCodUHE             List        Lista contendo o codigo das UHEs
        listaNomeUHE            List        Lista contendo o nome das UHEs

    funcoes:
        carregaInviab           le as inviablidades
        getTipoInviab           retorna o tipo da inviabilidade (mneumonico do DECOMP)
        getLimiteInviab         retorna se eh limite inferior ou superior
        getPatamarInviab        retorna o patamar da inviabilidade
        incluirInviab           inclui a inviabilidade nas listas
        inicializaListaUHEs     rotina que le e inicializa a lista de usinas
   """

    def __init__(self):
        # inicializa as listas
        self.listaTipo = []
        self.listaCod = []
        self.listaEtapa = []
        self.listaCenario = []
        self.listaLimite = []
        self.listaPatamar = []
        self.listaValor = []
        self.listaCodUHE = []

    def carregaInviab(self, versaoDecomp, usinas):

        valida = True

        # abre o arquivo de log, para informar o andamento do processo de leitura das inviablidades
        with open('retirainviab.log', 'a') as arqRetInviab:
            # informa que esta na etapa de leitura das regras
            arqRetInviab.write('\nINICIO DA ETAPA DE LEITURA DAS INVIABILIDADES\n')
        try:
            # obtem o nome do arquivo
            arquivo = glob.glob('inviab_unic.*')
            # tenta abrir o arquivo
            with open(arquivo[0], 'r') as arqInviab:
                # vai para a simulacao final
                linha = arqInviab.readline()
                while 'SIMULACAO FINAL:' not in linha:
                    linha = arqInviab.readline()
                # pula 3 linhas
                for i in range(3): arqInviab.readline()
                iInviab = 0
                # varre o arquivo
                for linha in arqInviab:

                    tipoInviab = 'false'
                    codigoInviab = -1

                    if not('DEFICIT' in linha):
                        # verifica qual o tipo da inviab
                        tipoInviab = self.getTipoInviab(linha)
                        # verifica qual a etapa
                        etapaInviab = int(linha[8:10])
                        # verifica qual a etapa
                        cenarioInviab = int(linha[16:19])
                        # verifica qual o codigo da inviabilidade
                        codigoInviab = self.getCodigoInviab(linha, tipoInviab, versaoDecomp, usinas)
                        # verifica se eh limite superior ou inferior
                        limiteInviab = self.getLimiteInviab(linha, tipoInviab, versaoDecomp)
                        # verifica qual o patamar
                        patamarInviab = self.getPatamarInviab(linha, tipoInviab, versaoDecomp)
                        # verifica o valor da inviabilidade
                        valorInviab = float(linha[99:109])

                    # soh inclui se achou a correspondencia do tipo da inviabilidade, ou se achou o codigo
                    if ('false' not in tipoInviab) or not(codigoInviab == -1):
                        #verifica se deve incluir nas listas
                        iInviab = self.incluirInviab(tipoInviab, etapaInviab, cenarioInviab, codigoInviab, limiteInviab, patamarInviab, valorInviab, iInviab)

            # abre o arquivo de log, para informar informa quantas regras foram lidas
            with open('retirainviab.log', 'a') as arqRetInviab:
                arqRetInviab.write('Foram lidas ' + str(iInviab) + ' inviabilidades\n')

        # se nao consegui eh por que ele nao existe
        except IOError:
            #se nao achou o arquivo, imprime no log e sai da rotina
            print('arquivo inviab_unic.* nao encontrado')
            # escreve no aquivo de Log que nao encontrou o arquivo
            with open('retirainviab.log', 'a') as arqRetInviab:
                arqRetInviab.write('ERRO: arquivo de inviabilidades inviab_unic.* nao encontrado, o processo sera interrompido\n')
            valida = False

        return valida

    # funcao que retorna qual o tipo da inviabilidade
    def getTipoInviab(self, linha):

        # verifica se eh RE
        if 'RESTRICAO ELETRICA' in linha:
            tipoRestricao = 'RE'
        elif 'RHQ' in linha:
            tipoRestricao = 'HQ'
        elif 'IRRIGACAO' in linha:
            tipoRestricao = 'TI'
        elif 'RHV' in linha:
            tipoRestricao = 'HV'
        # trata a evaporacao
        elif 'EVAPORACAO' in linha:
            tipoRestricao = 'EV'
        elif 'DEF. MINIMA' in linha:
            tipoRestricao = 'DM'
        else:
            print('Tipo da inviabilidade nao encontrado')
            # escreve no log
            with open('retirainviab.log', 'a') as arqRetInviab:
                #arqRetInviab.write(
                #    'ERRO: Tipo de inviabilidade nao encontrado, o processo sera interrompido: ' + linha + '\n')
                arqRetInviab.write(
                    'ERRO: Tipo de inviabilidade nao encontrado: ' + linha + '\n')
            tipoRestricao = 'false'

        return tipoRestricao

    # funcao que retorna o codigo da inviabilidade
    def getCodigoInviab(self, linha, tipoInviab, versaoDecomp, usinas):

        codigo = -1
        nome_usina=""

        # se for RE
        if 'RE' in tipoInviab:
            if(versaoDecomp < 276):
                codigo = int(linha[42:45])
            else:
                codigo = int(linha[42:46])
        # se for HQ
        elif 'HQ' in tipoInviab:
            codigo = int(linha[27:30])
        # se for HV
        elif 'HV' in tipoInviab:
            codigo = int(linha[27:30])
        # se for IT
        elif 'TI' in tipoInviab:
            # varre a lista com o nome das UHEs
            for index in range(1,320):
                if usinas[index].nome.strip(" ") == linha[40:52].strip(" "):
                    codigo = usinas[index].numero
                    nome_usina=(usinas[index].nome.strip(" "))
            # se nao achou a UHE escreve no aquivo de Log que nao encontrou
            if codigo == -1:
                with open('retirainviab.log', 'a') as arqRetInviab:
                    arqRetInviab.write('ERRO: nao foi encontrado o codigo da UHE  ' + linha[40:52] + ' no arquivo nomeuhe.txt\n')
        #se for evaporacao
        elif 'EV' in tipoInviab:
            # varre a lista com o nome das UHEs
            for index in range(1,320):
                if usinas[index].nome.strip(" ") == linha[41:53].strip(" "):
                    codigo = usinas[index].numero
                    nome_usina=(usinas[index].nome.strip(" "))
            # se nao achou a UHE escreve no aquivo de Log que nao encontrou
            if codigo == -1:
                with open('retirainviab.log', 'a') as arqRetInviab:
                    arqRetInviab.write('ERRO: nao foi encontrado o codigo da UHE  ' + linha[41:53] + ' no arquivo nomeuhe.txt\n')
        #se for defluencia minima
        elif 'DM' in tipoInviab:
            # varre a lista com o nome das UHEs
            for index in range(1,320):
                if usinas[index].nome.strip(" ") == linha[52:64].strip(" "):
                    codigo = usinas[index].numero
                    nome_usina=(usinas[index].nome.strip(" "))
            # se nao achou a UHE escreve no aquivo de Log que nao encontrou
            if codigo == -1:
                with open('retirainviab.log', 'a') as arqRetInviab:
                    arqRetInviab.write('ERRO: nao foi encontrado o codigo da UHE  ' + linha[52:64] + ' no arquivo nomeuhe.txt\n')

        return codigo, nome_usina

    #funcao que retorna se eh limite superior (1) ou inferior (0)
    def getLimiteInviab(self, linha, tipoInviab, versaoDecomp):

        # assume que eh limite inferior
        limite = 0

        #verifica se eh limite inferior
        # se for RE
        if 'RE' in tipoInviab:
            if(versaoDecomp < 276):
                if 'SUP' in linha[56:64]:
                    limite = 1
            else:
                if 'SUP' in linha[57:65]:
                    limite = 1
        # se for HQ
        elif 'HQ' in tipoInviab:
            if 'SUP' in linha[48:56]:
                limite = 1
        # se for HV
        elif 'HV' in tipoInviab:
            if 'SUP' in linha[50:58]:
                limite = 1
        return limite

    #funcao que retorna o patamar
    def getPatamarInviab(self, linha, tipoInviab, versaoDecomp):

        patamar = 0

        #verifica qual eh
        # se for RE
        if 'RE' in tipoInviab:
            if(versaoDecomp < 276):
                patamar = int(linha[54:55])
            else:
                patamar = int(linha[55:56])
        # se for DM
        elif 'DM' in tipoInviab:
            patamar = int(linha[44:45])
        # se for HQ
        elif 'HQ' in tipoInviab:
            patamar = int(linha[66:67])

        return patamar

    # verifica se deve incluir a informacao da inviabilidade, se precisar inclui ou atualiza a informacao
    def incluirInviab(self, tipoInviab, etapaInviab, cenarioInviab, codigoInviab, limiteInviab, patamarInviab, valorInviab, iInviab):

        achou = False
        # varre todas as inviabilidades, verificando se essa informacao jah foi incluida
        for index in range(len(self.listaTipo)):
            if self.listaTipo[index] == tipoInviab:
                if self.listaCod[index] == codigoInviab:
                    if self.listaEtapa[index] == etapaInviab:      
                        if self.listaLimite[index] == limiteInviab:
                            if self.listaPatamar[index] == patamarInviab:
                                if self.listaValor[index] < valorInviab:
                                    self.listaValor[index] = valorInviab
                                    self.listaCenario[index] = cenarioInviab
                                achou = True
                                break

        # se nao achou inclui na lista
        if not achou:
            self.listaTipo.append(tipoInviab)
            self.listaCod.append(codigoInviab)
            self.listaEtapa.append(etapaInviab)
            self.listaCenario.append(cenarioInviab)
            self.listaLimite.append(limiteInviab)
            self.listaPatamar.append(patamarInviab)
            self.listaValor.append(valorInviab)
            iInviab += 1

        return iInviab

    #imprime todas as inviabilidades
    def ecoInviab(self):
        for index in range(len(self.listaTipo)):
            print(self.listaTipo[index])
            print(self.listaCod[index])
            print(self.listaEtapa[index])
            print(self.listaCenario[index])
            print(self.listaLimite[index])
            print(self.listaPatamar[index])
            print(self.listaValor[index])

