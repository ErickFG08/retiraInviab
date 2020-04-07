# -*- coding: latin-1 -*-

"""
    rotinas responsaveis pela retirada das inviabilidades
"""

from trataInviab import *
from inviab import *

import funcoes
import importaHidr
import math
import sys

import funcoes
import importaRelato
import importaRelato2

import arrumaDadger

# funcao de chamada para retirar as inviabilidades do DECOMP
def retiraInviab(inviab, regras, iteracao, usinas, ultima_etapa):

    valida = True

    # abre o arquivo de log, para informar o andamento do processo
    with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
        # informa que esta na etapa de retirada das inviabilidades
        arqRetInviab.write('\nINICIO DA ETAPA DE RETIRAR AS INVIABILIDADES\n')

    duracao = funcoes.cDADGER()
    duracao.obtemDuracaoPatamares()

    #varre todas as inviabilidades
    for index in range(len(inviab.listaTipo)):
        # variavel que informa se o valor foi flexibilizado
        flex = False

        # obtem o indice da regra para retirar essa inviabilidade
        indice = getIndiceRegra(inviab, index, regras, iteracao)

        #verifica se achou a regra de flexibilizacao
        if indice > -1:
            # calcula o valor que deve ser retirado (faz as equivalencias de unidades vazao -> volume, vazao -> geracao, etc...)
            valor = getValorFlexibilizar(inviab, index, regras, indice, duracao, usinas, ultima_etapa)
            #procura no DADGER a restricao que deve flexibilizar e flexibiliza
            flex = flexibilizaDADGER(inviab, index, regras, indice, valor, usinas, iteracao)

        # se nao for informa o erro no log
        else:
            # abre o arquivo de log, para informar o erro
            with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
                # informa que nao achou a regra
                if indice == -1:
                    arqRetInviab.write('ERRO: regra de flexibilizacao da ' + inviab.listaTipo[index] + ' ' + str("%3i" % (inviab.listaCod[index][0])) + ' etapa ' + str(inviab.listaEtapa[index]) + ' nao encontrada, o processo sera interrompido\n')
                    valida = False
                elif indice == -2:                  
                    arqRetInviab.write('ERRO: regra de flexibilizacao da ' + inviab.listaTipo[index] + ' ' + str("%3i" % (inviab.listaCod[index][0])) + ' etapa ' + str(inviab.listaEtapa[index]) + ' iteracao ' + str(iteracao) + ' nao encontrada\n')

    return valida

# funcao que retorna o indice da regra a ser flexibilizada
def getIndiceRegra(inviab, indiceInviab, regras, iteracao):

    etapa = 0
    resp = -1
    iterAnterior=0
    # varre todas as regras
    for indice in range(len(regras.listaTipoRestr)):
        #verifica se eh a regra correta
        # se for o mesmo tipo
        if regras.listaTipoRestr[indice] == inviab.listaTipo[indiceInviab]:
            # se for o mesmo codigo
            if (regras.listaCodRestr[indice] == inviab.listaCod[indiceInviab][0]) or (regras.listaCodRestr[indice] == 0):
                # se for no mesmo limite (superior ou inferior)
                if regras.listaLimite[indice] == inviab.listaLimite[indiceInviab]:
                    # se for estiver na mesma etapa ou em uma anterior
                    if (regras.listaEtapaRestr[indice] <= inviab.listaEtapa[indiceInviab]) and (etapa <= inviab.listaEtapa[indiceInviab]):
                        # se chegou ate esta etapa signica que a regra existe porem, talvez em outra iteracao
                        if resp == -1:
                            resp = -2
                        # se for na mesma iteracao ou em uma menor
                        if (regras.listaIteracao[indice] <= iteracao and iterAnterior <= regras.listaIteracao[indice]):
                            resp = indice
                            etapa = regras.listaEtapaRestr[indice]
                            iterAnterior = regras.listaIteracao[indice]

    return resp

# funcao que retorna o valor a ser flexibilizado, fazendo as equivalencias entre vazao<->volume, vazao<->geracao e volume<->geracao
def getValorFlexibilizar(inviab, index, regras, indice, duracao, usinas_hidr, ultima_etapa):

    # se as duas forem de vazao, retorna o proprio valor
    if inviab.listaTipo[index] == 'TI' and regras.listaTipoRestrFlex[indice] == 'HQ':
        valor = round(inviab.listaValor[index],1) + 0.1
    elif inviab.listaTipo[index] == 'HQ' and regras.listaTipoRestrFlex[indice] == 'TI':
        valor = round(inviab.listaValor[index],2) + 0.01
    # se for geracao para vazao
    elif inviab.listaTipo[index] == 'RE' and (regras.listaTipoRestr[indice] == 'TI' or regras.listaTipoRestrFlex[indice] == 'HQ'):

        relato1 = glob.glob('relato.*')
        relato2 = glob.glob('relato2.*')

        prodt = 1

        i = int(regras.listaUsinaEnvolvida[indice])

        nome_usina = str(usinas_hidr[i].nome)

        if inviab.listaEtapa[index] != ultima_etapa:

            prodt = importaRelato.c_relato().leRelato(relato1[0], nome_usina)

        elif inviab.listaEtapa[index] == ultima_etapa:

            prodt = importaRelato2.c_relato2().leRelato2(relato2[0], nome_usina, inviab.listaCenario[index])

        valor = inviab.listaValor[index]/prodt

        if regras.listaTipoRestrFlex[indice] == 'TI':
            valor = round(valor,2) + 0.01
        elif regras.listaTipoRestrFlex[indice] == 'HQ':
            valor = round(valor,1) + 0.1

    # se for vazao para geracao
    elif (inviab.listaTipo[index] == 'TI' or inviab.listaTipo[index] == 'HQ') and regras.listaTipoRestrFlex[indice] == 'RE':

        relato1 = glob.glob('relato.*')
        relato2 = glob.glob('relato2.*')

        prodt = 1

        i = int(regras.listaUsinaEnvolvida[indice])

        nome_usina = str(usinas_hidr[i].nome)

        if inviab.listaEtapa[index] != ultima_etapa:

            prodt = importaRelato.c_relato().leRelato(relato1[0], nome_usina)

        elif inviab.listaEtapa[index] == ultima_etapa:

            prodt = importaRelato2.c_relato2().leRelato2(relato2[0], nome_usina, inviab.listaCenario[index])

        valor = round(inviab.listaValor[index]*prodt,1) + 0.1

    #se for vazao para volume
    elif inviab.listaTipo[index] == 'TI' and regras.listaTipoRestrFlex[indice] == 'HV':
        
        # passa de m3/s para hm3
        valor = inviab.listaValor[index]*(60*60*duracao.total)*0.000001

        valor = round(valor,2) + 0.01

    #se for vazao para volume
    elif inviab.listaTipo[index] == 'HQ' and regras.listaTipoRestrFlex[indice] == 'HV':

        # passa de m3/s para hm3
        if inviab.listaPatamar[index] == 1:
            valor = inviab.listaValor[index]*(60*60*duracao.pesada)*0.000001
        elif inviab.listaPatamar[index] == 2:
            valor = inviab.listaValor[index]*(60*60*duracao.media)*0.000001
        elif inviab.listaPatamar[index] == 3:
            valor = inviab.listaValor[index]*(60*60*duracao.leve)*0.000001

        valor = round(valor,2) + 0.01

    #se for volume para vazao
    elif inviab.listaTipo[index] == 'HV' and (regras.listaTipoRestrFlex[indice] == 'TI' or regras.listaTipoRestrFlex[indice] == 'HQ'):
        # passa de m3/s para hm3
        valor = inviab.listaValor[index]/((60*60*duracao.total)*0.000001)
        if regras.listaTipoRestrFlex[indice] == 'TI':
            valor = round(valor,2) + 0.01
        elif regras.listaTipoRestrFlex[indice] == 'HQ':
            valor = round(valor,1) + 0.1

    # evaporacao para AC
    elif inviab.listaTipo[index] == 'EV' and regras.listaTipoRestrFlex[indice] == 'AC':
        valor = inviab.listaValor[index]
    # evaporacao para evaporacao
    elif inviab.listaTipo[index] == 'EV' and regras.listaTipoRestrFlex[indice] == 'EV':
        valor = 0
    # Defluencia minima para AC
    elif inviab.listaTipo[index] == 'DM' and regras.listaTipoRestrFlex[indice] == 'DM':

        if inviab.listaPatamar[index] == 1:
            valor = math.ceil(inviab.listaValor[index]*(duracao.pesada/duracao.total))
        elif inviab.listaPatamar[index] == 2:
            valor = math.ceil(inviab.listaValor[index]*(duracao.media/duracao.total))
        elif inviab.listaPatamar[index] == 3:
            valor = math.ceil(inviab.listaValor[index]*(duracao.leve/duracao.total))      

    # Defluencia maxima para porcentagem do VE
    elif inviab.listaTipo[index] == 'HQ' and regras.listaTipoRestrFlex[indice] == 'VE':
        
        # passa de m3/s para hm3
        if inviab.listaPatamar[index] == 1:
            volume_hm3 = inviab.listaValor[index]*(60*60*duracao.pesada)*0.000001
        elif inviab.listaPatamar[index] == 2:
            volume_hm3 = inviab.listaValor[index]*(60*60*duracao.media)*0.000001
        elif inviab.listaPatamar[index] == 3:
            volume_hm3 = inviab.listaValor[index]*(60*60*duracao.leve)*0.000001

        volume_util = usinas_hidr[regras.listaCodRestrFlex[indice]].volUtil
        valor = round(100*volume_hm3/volume_util,2) + 0.01

    # se as duas forem iguais, retorna o proprio valor
    elif inviab.listaTipo[index] == regras.listaTipoRestrFlex[indice]:

        if inviab.listaTipo[index] == 'VE' or inviab.listaTipo[index] == 'TI' or inviab.listaTipo[index] == 'HV':
            valor = round(inviab.listaValor[index],2) + 0.01
        elif inviab.listaTipo[index] == 'RE' or inviab.listaTipo[index] == 'HA' or inviab.listaTipo[index] == 'HQ':
            valor = round(inviab.listaValor[index],1) + 0.1
        elif inviab.listaTipo[index] == 'AC':
            valor = inviab.listaValor[index]
        else:
            valor = -1

    else:
        valor = -1

    return valor

#funcao que retira o valor da inviabilizadade no DADGER
def flexibilizaDADGER(inviab, index, regras, indice, valor, usinas_hidr, iteracao):

    import glob
    import os

    flex = False

    try:
        # obtem o nome do arquivo
        arquivo = glob.glob('dadger.*')

        # tenta abrir o arquivo
        with open(arquivo[0], 'r', encoding="latin_1") as arqDADGER:
            # abre o arquivo que sera escrito o novo DADGER
            with open('dadger_novo.dat', 'w', encoding="latin_1") as arqDADGERnovo:
                #le a linha
                linha = arqDADGER.readline()
                #escreve a linha
                arqDADGERnovo.write(linha)
                # procura a restricao
                # se for restricao Eletrica
                if regras.listaTipoRestrFlex[indice] == 'RE':
                    FlexREHQ(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, 'RE', 'LU')
                # se for restricao de Vazao
                elif regras.listaTipoRestrFlex[indice] == 'HQ':
                    FlexREHQ(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, 'HQ', 'LQ')
                # se for restricao de volume
                elif regras.listaTipoRestrFlex[indice] == 'HV':
                    FlexHVHA(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, 'HV', 'LV')
                # se for restricao de afluencia
                elif regras.listaTipoRestrFlex[indice] == 'HA':
                    FlexHVHA(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, 'HA', 'LA')
                # se for restricao de irrigacao
                elif regras.listaTipoRestrFlex[indice] == 'TI':
                    FlexTI(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor)
                # se for restricao de vazao minima
                elif regras.listaTipoRestrFlex[indice] == 'DM':
                    FlexDM(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, usinas_hidr)
                # evaporacao para vazao minima
                elif regras.listaTipoRestrFlex[indice] == 'EV' and inviab.listaTipo[index] != 'EV':
                    FlexDM(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, usinas_hidr)
                # se for restricao de evaporacao para tirar a propria evaporacao
                elif regras.listaTipoRestrFlex[indice] == 'EV' and inviab.listaTipo[index] == 'EV':
                    FlexEV(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, usinas_hidr)
                # se for restricao de volume de Espera               
                elif regras.listaTipoRestrFlex[indice] == 'VE':
                    FlexVE(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor)
                else:
                    # varre o arquivo
                    while True:
                        linha = arqDADGER.readline()
                        if linha == '':
                            break
                        #escreve a linha
                        arqDADGERnovo.write(linha)

        # deleta o dadger
        os.remove(arquivo[0])
        # renomeia o dadger novo
        os.rename('dadger_novo.dat', arquivo[0])
        # chama funcao que compacta o dadger
        #arrumaDadger.retrai_dadger(arquivo[0])
        # informa que flexibilizou a restricao
        with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
            if inviab.listaTipo[index] == 'DM' and regras.listaTipoRestrFlex[indice] == 'DM':
                i = int(inviab.listaCod[index][0])
                arqRetInviab.write('Restricao de vazao minima da usina ' + usinas_hidr[i].nome + 'em' + str("%3i" % valor) + ' m3/s\n')
            else:
                arqRetInviab.write(
                    'Restricao ' + inviab.listaTipo[index] + ' ' + str("%3i" % (inviab.listaCod[index][0])) + ' etapa ' +
                    str(inviab.listaEtapa[index]) + ' patamar ' + str(inviab.listaPatamar[index]) +' flexibilizada em ' + str("%.2f" % valor) +
                    ' na restricao ' + regras.listaTipoRestrFlex[indice] + ' ' + str("%3i" % (regras.listaCodRestrFlex[indice])) + '\n')

   # se nao conseguiu eh por que ele nao existe
    except IOError:
        # se nao achou o arquivo, imprime no log e sai da rotina
        print('arquivo dadger.* nao encontrado')
        # escreve no arquivo de Log que nao encontrou o arquivo
        with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
            arqRetInviab.write(
                'ERRO: arquivo dadger.* nao encontrado, o processo sera interrompido\n')
            flex = False

    return flex

# rotina para retirar flexibilizacao de RE, HQ
def FlexREHQ(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, MneumoRestr, MneumoLimite):

    fin = open(arqDADGER.name, 'r+', encoding = "latin_1")

    fout = open(arqDADGERnovo.name, 'w+', encoding = "latin_1")

    #se a regra for para retirar do codigo 0, utiliza o codigo da inviabilidade

    if regras.listaCodRestrFlex[indice] == 0:

        codigoRegra = inviab.listaCod[index][0]

    else:

        codigoRegra = regras.listaCodRestrFlex[indice]

    tresPat = False

    #verifica se a inviabilidade original nao eh para os 3 patamares

    if inviab.listaTipo[index] != 'RE' and inviab.listaTipo[index] != 'HQ':

        tresPat = True

    linha_anterior = ""

    for linha in fin:
        
        if MneumoRestr + '  ' + str("%3i" % codigoRegra) in linha[0:7]:

            if not 'Flex' in linha_anterior:
        
                fout.write('& Flexibilizado para convergencia na etapa ' + str(inviab.listaEtapa[index]) + '\n')

                fout.write(linha)

                linha_anterior = linha
            
            else:

                fout.write(linha)

        elif MneumoLimite + '  ' + str("%3i" % codigoRegra) + '   ' + str(inviab.listaEtapa[index]) in linha[0:11]:

            novaLinha = linha[0:10] + str(inviab.listaEtapa[index]) + '   '

            # varre os 3 patamares

            for pat in [0, 1, 2]:
                # limite inferior
                if regras.listaLimiteFlex[indice] == 0:
                    # verifica qual o patamar
                    if inviab.listaPatamar[index] == pat + 1 or tresPat:
                        if float(linha[14 + 20 * pat : 24 + 20 * pat]) - valor >= 0:
                            novaLinha += "%10.1f" % (float(linha[14 + 20 * pat : 24 + 20 * pat]) - valor)
                        else:
                            novaLinha += "       0.0"
                    else:
                        novaLinha += linha[14 + 20 * pat : 24 + 20 * pat]
                else:
                    novaLinha += linha[14 + 20 * pat : 24 + 20 * pat]
                # limite superior
                if regras.listaLimiteFlex[indice] == 1:
                    # verifica qual o patamar
                    if inviab.listaPatamar[index] == pat + 1 or tresPat:
                        novaLinha += "%10.1f" % (float(linha[24 + 20 * pat : 34 + 20 * pat]) + valor)
                    else:
                        novaLinha += linha[24 + 20 * pat : 34 + 20 * pat]
                else:
                    novaLinha += linha[24 + 20 * pat : 34 + 20 * pat]

            # escreve a linha
            fout.write(novaLinha)

        else:
            fout.write(linha)
            linha_anterior = linha

    fin.close()

    fout.close()

# rotina para retirar flexibilizacao de HV e HA
def FlexHVHA(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, MneumoRestr, MneumoLimite):

    #se a regra for para retirar do codigo 0, utiliza o codigo da inviabilidade
    if regras.listaCodRestrFlex[indice] == 0:
        codigoRegra = inviab.listaCod[index][0]
    else:
        codigoRegra = regras.listaCodRestrFlex[indice]

    achou = False
    # varre o arquivo
    while True:
        linha = arqDADGER.readline()
        if not linha: break

        arqDADGERnovo.write(linha)
        if MneumoRestr + '  ' + str("%3i" % codigoRegra) in linha[0:7]:
            achou = True
            break
    if achou:
        # le 1 linhas do arquivo
        linha1 = arqDADGER.readline()
        # verifica se eh para escreve o comentario de flexibilizacao
        if not "Flexibilizado" in linha1:
            # escreve a linha
            arqDADGERnovo.write("& Flexibilizado para convergencia\n")
        else:
            #copia a linha do comentario
            arqDADGERnovo.write(linha1)
            # le 1 linhas do arquivo
            linha1 = arqDADGER.readline()
        # le 2 linhas do arquivo
        linha2 = arqDADGER.readline()
        # verifica se a linha 2 eh informacao dos limites
        if linha2[0:2] == MneumoLimite:
            # se for a restricao na primeira etapa
            if inviab.listaEtapa[index] == 1:
                novaLinha = linha1[0:9] + ' 1   '
                # limite inferior
                if regras.listaLimiteFlex[indice] == 0:
                    if float(linha1[14:24]) - valor >= 0:
                        novaLinha += "%10.2f" % (float(linha1[14:24]) - valor)
                    else:
                        novaLinha += "       0.0"
                else:
                    novaLinha += linha1[14:24]
                # limite superior
                if regras.listaLimiteFlex[indice] == 1:
                    novaLinha += "%10.2f" % (float(linha1[24:34]) + valor)
                else:
                    novaLinha += linha1[24:34]
                # coloca o enter
                novaLinha += '\n'
                # escreve a linha
                arqDADGERnovo.write(novaLinha)
                # escreve a restricao da segunda etapa
                arqDADGERnovo.write(linha2)
            else:
                novaLinha = linha2[0:9] + ' 2   '
                # limite inferior
                if regras.listaLimiteFlex[indice] == 0:
                    if float(linha2[14:24]) - valor >= 0:
                        novaLinha += "%10.2f" % (float(linha2[14:24]) - valor)
                    else:
                        novaLinha += "       0.0"
                else:
                    novaLinha += linha2[14:24]
                # limite superior
                if regras.listaLimiteFlex[indice] == 1:
                    novaLinha += "%10.2f" % (float(linha2[24:34]) + valor)
                else:
                    novaLinha += linha2[24:34]
                # coloca o enter
                novaLinha += '\n'
                # escreve a restricao da primeira etapa
                arqDADGERnovo.write(linha1)
                # escreve nova linha
                arqDADGERnovo.write(novaLinha)
        else:
            if inviab.listaEtapa[index] == 1:
                novaLinha = linha1[0:9] + ' 1   '
                novaLinha2 = linha1[0:9] + ' 2   ' + linha1[14:len(linha1)]
            else:
                novaLinha = linha1[0:9] + ' 2   '
            # limite inferior
            if regras.listaLimiteFlex[indice] == 0:
                if float(linha1[14:24]) - valor >= 0:
                    novaLinha += "%10.2f" % (float(linha1[14:24]) - valor)
                else:
                    novaLinha += "       0.0"
            else:
                novaLinha += linha1[14:24]
            # limite superior
            if regras.listaLimiteFlex[indice] == 1:
                novaLinha += "%10.2f" % (float(linha1[24:34]) + valor)
            else:
                novaLinha += linha1[24:34]
            # coloca o enter
            novaLinha += '\n'
            # se for a restricao na primeira etapa
            if inviab.listaEtapa[index] == 1:
                # escreve a linha
                arqDADGERnovo.write(novaLinha)
                # escreve a restricao da segunda etapa
                arqDADGERnovo.write(novaLinha2)
                # escreve a 'linha2'
                arqDADGERnovo.write(linha2)
            else:
                # escreve a restricao da primeira etapa
                arqDADGERnovo.write(linha1)
                # escreve nova linha
                arqDADGERnovo.write(novaLinha)
                # escreve a 'linha2'
                arqDADGERnovo.write(linha2)

        # varre o arquivo
        for linha in arqDADGER:
            # escreve a linha
            arqDADGERnovo.write(linha)
    else:
        # informa que nao achou a restricao
        with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
            arqRetInviab.write(
                'ERRO: Restricao ' + regras.listaTipoRestrFlex[indice] + ' ' + str("%3i" % (codigoRegra)) + ' etapa ' + str(regras.listaEtapaRestr[indice]) + ' nao encontrada no DADGER\n')

# rotina para retirar flexibilizacao de TI
def FlexTI(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor):

    #se a regra for para retirar do codigo 0, utiliza o codigo da inviabilidade
    if regras.listaCodRestrFlex[indice] == 0:
        codigoRegra = inviab.listaCod[index][0]
    else:
        codigoRegra = regras.listaCodRestrFlex[indice]

    achou = False

    # varre o arquivo
    for linha in arqDADGER:

        if 'TI  ' + str("%3i" % codigoRegra) in linha[0:7]:
            achou = True
            break
        else:
            # escreve a linha
            arqDADGERnovo.write(linha)
            if 'Flex' in linha:
                comentarioFlex = True
            else:
                comentarioFlex = False

    if achou:
        #escreve o comentario
        if not comentarioFlex:
            arqDADGERnovo.write('& Flexibilizado para convergencia\n')

        #comeca a escrever a nova linha
        novaLinha = linha[0:9]
        # verifica se eh no primeiro estagio
        if inviab.listaEtapa[index] == 1:
            # flexibiliza a restricao
            if float(linha[9:14]) - valor >= 0:
                novaLinha += "%5.2f" % (float(linha[9:14]) - valor)
            else:
                novaLinha += " 0.00"
            novaLinha += linha[14:19] + '\n'
        # se for segundo estagio
        else:
            # flexibiliza a restricao
            novaLinha += linha[9:14]
            if float(linha[14:19]) - valor >= 0:
                novaLinha += "%5.2f" % (float(linha[14:19]) - valor) + '\n'
            else:
                novaLinha += " 0.00\n"

         # escreve nova linha
        arqDADGERnovo.write(novaLinha)

        # varre o arquivo
        for linha in arqDADGER:
            # escreve a linha
            arqDADGERnovo.write(linha)
    else:
        # informa que nao achou a restricao
        with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
            arqRetInviab.write(
                'ERRO: Restricao ' + regras.listaTipoRestrFlex[indice] + ' ' + str("%3i" % codigoRegra) + ' etapa ' + str(regras.listaEtapaRestr[indice]) + ' nao encontrada no DADGER\n')

# rotina para retirar flexibilizacao de vazao minima
def FlexDM(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, usinas_hidr):

    #se a regra for para retirar do codigo 0, utiliza o codigo da inviabilidade
    if regras.listaCodRestrFlex[indice] == 0:
        codigoRegra = inviab.listaCod[index][0]
    else:
        codigoRegra = regras.listaCodRestrFlex[indice]

    achou1 = False
    achou2 = False

    # varre o arquivo
    while True:
        linha = arqDADGER.readline()
        if linha == '':
            break
        if 'AC' == linha[0:2] and 'VAZMIN' == linha[9:15] and linha[4:7] == str("%3i" % codigoRegra):
            achou1 = True
            break
        else:
            arqDADGERnovo.write(linha)    

    if achou1:

        valor_antigo = int(linha[16:24])

        # previne que o valor fique negativo
        if (valor_antigo - valor) < 0:
            valor_a_ser_usado = 0
        else:
            valor_a_ser_usado = valor_antigo - valor

        # escreve a linha
        novaLinha = 'AC  ' + str("%3i" % codigoRegra) + '  VAZMIN    ' + str("%5i" % (valor_a_ser_usado)) + '\n'
        arqDADGERnovo.write(novaLinha)
    
    else:

        arqDADGER.seek(0)
        arqDADGERnovo.seek(0)
        
        while True:
            linha = arqDADGER.readline()
            if linha == '':
                break
            if 'AC' == linha[0:2] and 'VAZMIN' == linha[9:15]:
                achou2 = True
                break
            else:
                arqDADGERnovo.write(linha)                  

    if achou2:

        arqDADGERnovo.write(linha)
        #escreve o comentario
        arqDADGERnovo.write('& Flexibilizado para convergencia - ' + str(inviab.listaCod[index][1]) + '\n')

        i = int(inviab.listaCod[index][0])
        vazao_minima = round(usinas_hidr[i].vazaoMin,0) 

        # escreve a linha
        novaLinha = 'AC  ' + str("%3i" % codigoRegra) + '  VAZMIN    ' + str("%5i" % (vazao_minima - valor)) + '\n'            
        arqDADGERnovo.write(novaLinha)

    # varre o arquivo
    while True:
        linha = arqDADGER.readline()
        if linha == '':
            break
        # le a 2 linha
        arqDADGERnovo.write(linha)

def FlexEV(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor, usinas_hidr):

    #se a regra for para retirar do codigo 0, utiliza o codigo da usina
    if regras.listaCodRestrFlex[indice] == 0:
        codigoRegra = inviab.listaCod[index][0]
    else:
        codigoRegra = regras.listaCodRestrFlex[indice]

    # varre o arquivo
    while True:
        linha = arqDADGER.readline()
        if linha == '':
            break
        elif 'UH' == linha[0:2] and linha[4:7] == str("%3i" % codigoRegra):
            novaLinha = linha[0:39] + '0                              ' + '\n'
            arqDADGERnovo.write(novaLinha)

    # varre o arquivo
    while True:
        linha = arqDADGER.readline()
        if linha == '':
            break
        # le a 2 linha
        arqDADGERnovo.write(linha)

# rotina para retirar flexibilizacao de VE
def FlexVE(arqDADGER, arqDADGERnovo, inviab, index, regras, indice, valor):

    achou = False

    #se a regra for para retirar do codigo 0, utiliza o codigo da inviabilidade
    if regras.listaCodRestrFlex[indice] == 0:
        codigoRegra = inviab.listaCod[index][0]
    else:
        codigoRegra = regras.listaCodRestrFlex[indice]

    # varre o arquivo
    for linha in arqDADGER:

        if 'VE  ' + str("%3i" % codigoRegra) in linha[0:7]:
            achou = True
            break
        else:
            # escreve a linha
            arqDADGERnovo.write(linha)
            if 'Flexibilizado' in linha:
                comentarioFlex = True
            else:
                comentarioFlex = False

    if achou:
        #escreve o comentario
        if not comentarioFlex:
            arqDADGERnovo.write('& Flexibilizado para convergencia\n')

        #comeca a escrever a nova linha
        novaLinha = linha[0:9]
        # verifica se eh no primeiro estagio
        if inviab.listaEtapa[index] == 1:
            # flexibiliza a restricao
            if float(linha[9:14]) + valor <= 100:
                novaLinha += "%5.2f" % (float(linha[9:14]) + valor)
            else:
                novaLinha += "100.0"
            novaLinha += linha[14:19] + '\n'
        # se for segundo estagio
        else:
            # flexibiliza a restricao
            novaLinha += linha[9:14]
            if float(linha[14:19]) + valor <= 100:
                novaLinha += "%5.2f" % (float(linha[14:19]) + valor) + '\n'
            else:
                novaLinha += "100.0\n"

         # escreve nova linha
        arqDADGERnovo.write(novaLinha)

        # varre o arquivo
        for linha in arqDADGER:
            # escreve a linha
            arqDADGERnovo.write(linha)
    else:
        # informa que nao achou a restricao
        with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
            arqRetInviab.write(
                'ERRO: Restricao ' + regras.listaTipoRestrFlex[indice] + ' ' + str("%3i" % codigoRegra) + ' etapa ' + str(regras.listaEtapaRestr[indice]) + ' nao encontrada no DADGER\n')
