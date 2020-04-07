# -*- coding: latin-1 -*-

"""
    rotinas responsaveis pela retirada dos intercambios
"""

import funcoes
import math
import sys

# funcao de chamada para retirar as inviabilidades do DECOMP
def trataIntercambio(iteracao):

    import glob
    from shutil import copyfile

    # testa se existe sumario
    valida = True
    # testa se foi flexibilizado
    flex = False

    sumario = glob.glob('sumario.*')
    dadger = glob.glob('dadger.*')

    # testa se existe sumario
    try:
    # abre o arquivo sumário para leitura dos intercâmbios
        with open(sumario[0], 'r') as arqSumario:
            # varre as linhas para pegar dados
            for line in arqSumario:
                if '         S         2' in line:
                    ini_Sul = float(line[22:30].strip())
                    fim_Sul = float(line[30:-1].strip())
                    delta_Sul = fim_Sul - ini_Sul
                elif 'SE-IV   Media' in line:
                    SEIV = -1*float(line.split(' ')[-1])
                elif 'IV-S    Media' in line:
                    IVS = float(line.split(' ')[-1])
                elif 'SE-NE   Media' in line:
                    SENE = -1*float(line.split(' ')[-1])
                elif 'NE-FC   Media' in line:
                    NEFC = -1*float(line.split(' ')[-1])
                    break
    # se erro, 'valida' é falso e partira para próxima iteração
    except IOError:
        valida = False

    # abre dadger para obter limite do intercâmbio IV-SE
    with open(dadger[0], 'r') as arqDadger:
        # varre as linhas para pegar dados
        for line in arqDadger:
            if 'IA   1   SE   IV' in line:
                limiteSEIV = float(line.split(' ')[-1])
                break

    # testa loop de energia no NE
    if (SENE > 0) and (NEFC > 0):
        if abs(SENE - NEFC) > 0:
            #procura no DADGER a restricao que deve flexibilizar e flexibiliza
            flex = flexibilizaDADGER('NE   FC', iteracao)
        elif abs(NEFC - SENE) > 0:
            #procura no DADGER a restricao que deve flexibilizar e flexibiliza
            flex = flexibilizaDADGER('SE   NE', iteracao)

    # testa se Sul encheu e intercâmbio em Ivaiporã
    if ((delta_Sul > 10) and (IVS > 500) and (SEIV < limiteSEIV)):
        #procura no DADGER a restricao que deve flexibilizar e flexibiliza
        flex = flexibilizaDADGER('IV   S', iteracao)

    # se existe sumario (valida) e o intercambio foi flexibilizado (flex), mais uma iteracao
    if (valida) and (flex):
        segue = True
    # se não, o caso é dado como convergido
    else:
        segue = False
    return segue


#funcao que retira o valor da inviabilizadade no DADGER
def flexibilizaDADGER(nome_intercambio, iteracao):

    import glob
    import os
    from shutil import copyfile

    flex = False

    try:
        from shutil import copyfile
        # obtem o nome do arquivo

        arquivo_dadger = glob.glob('dadger.*')
        arquivo_sumario = glob.glob('sumario.*')
        arquivo_relato = glob.glob('relato.*')
        arquivo_relato2 = glob.glob('relato2.*')
        arquivo_inviab_unic = glob.glob('inviab_unic.*')

        # faz uma copia do dadger
        nome_explodido_dadger = arquivo_dadger[0].split('.')
        copyfile(arquivo_dadger[0], "dadger_" + str(iteracao) + "_" + "." + str(nome_explodido_dadger[-1]))
		
        # faz uma copia do sumario
        nome_explodido_sumario = arquivo_sumario[0].split('.')
        copyfile(arquivo_sumario[0], "sumario_" + str(iteracao) + "_" + "." + str(nome_explodido_sumario[-1]))

        # apaga o sumario para poder rodar novamente
        os.remove(arquivo_sumario[0])

        # faz uma copia do relato
        nome_explodido_relato = arquivo_relato[0].split('.')
        copyfile(arquivo_relato[0], "relato_" + str(iteracao) + "_" + "." + str(nome_explodido_relato[-1]))

        # faz uma copia do relato 2
        nome_explodido_relato2 = arquivo_relato2[0].split('.')
        copyfile(arquivo_relato2[0], "relato2_" + str(iteracao) + "_" + "." + str(nome_explodido_relato2[-1]))

        # faz uma copia do inviab_unic
        nome_explodido_inviab_unic = arquivo_inviab_unic[0].split('.')
        copyfile(arquivo_inviab_unic[0], "inviab_unic_" + str(iteracao) + "_" + "." + str(nome_explodido_inviab_unic[-1]))

        # tenta abrir o arquivo
        with open(arquivo_dadger[0], 'r') as arqDADGER:
            # abre o arquivo que sera escrito o novo DADGER
            with open('dadger_novo.dat', 'w') as arqDADGERnovo:
                #le a linha
                linha = arqDADGER.readline()
                #escreve a linha
                arqDADGERnovo.write(linha)
                # procura a restricao
                flex = FlexINT(arqDADGER, arqDADGERnovo, nome_intercambio)
                # varre o arquivo
                if not flex:
                    while True:
                        linha = arqDADGER.readline()
                        if linha == '':
                            break
                        #escreve a linha
                        arqDADGERnovo.write(linha)

        # deleta o dadger
        os.remove(arquivo_dadger[0])
        # renomeia o dadger novo
        os.rename('dadger_novo.dat', arquivo_dadger[0])
        # informa que flexibilizou a restricao
        with open('retirainviab.log', 'a') as arqRetInviab:
            arqRetInviab.write(
                'Restricao de intercambio ' + str(nome_intercambio) + ' flexibilizada \n')

   # se nao conseguiu eh por que ele nao existe
    except IOError:
        # se nao achou o arquivo, imprime no log e sai da rotina
        print('arquivo dadger.* nao encontrado')
        # escreve no aquivo de Log que nao encontrou o arquivo
        with open('retirainviab.log', 'a') as arqRetInviab:
            arqRetInviab.write(
                'ERRO: arquivo dadger.* nao encontrado, o processo sera interrompido\n')
            flex = False

    return flex


# rotina para retirar flexibilizacao de Intercambio
def FlexINT(arqDADGER, arqDADGERnovo, nome_intercambio):

    achou = False

    # varre o arquivo
    for linha in arqDADGER:

        if 'IA   1   ' + str(nome_intercambio) in linha:
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
        novaLinha = linha[0:19]
        # se for IV S, flexibiliza o DE -> PARA
        if nome_intercambio == 'IV   S':
            # flexibiliza a restricao
            novaLinha += "%10.1f" % (float(500))
            novaLinha += linha[29:39]
            novaLinha += "%10.1f" % (float(500))
            novaLinha += linha[49:59]
            novaLinha += "%10.1f" % (float(500))
            novaLinha += linha[69:79] + '\n'
        # se for os demais, flexibiliza o PARA -> DE
        else:
            novaLinha += linha[19:29]
            novaLinha += "%10.1f" % (float(0))
            novaLinha += linha[39:49]
            novaLinha += "%10.1f" % (float(0))
            novaLinha += linha[59:69]
            novaLinha += "%10.1f" % (float(0)) + '\n'

         # escreve nova linha
        arqDADGERnovo.write(novaLinha)
        # repete a linha antiga e troca o estágio para 2
        novalinha2 = str('IA   2') + linha[6:len(linha)-1] + '\n'
        arqDADGERnovo.write(novalinha2)

        # varre o arquivo
        for linha in arqDADGER:
            # escreve a linha
            arqDADGERnovo.write(linha)
    else:
        # informa que nao achou a restricao
        with open('retirainviab.log', 'a') as arqRetInviab:
            arqRetInviab.write(
                'ERRO: Restricao de intercambio ' + str(nome_intercambio) + ' nao encontrada no DADGER\n')
    return achou