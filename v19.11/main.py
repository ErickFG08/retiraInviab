#!/usr/bin/env python
# -*- coding: latin-1 -*-

'''
    Programa retiraInviab
        retira as inviabilidades do DECOMP apos o caso rodado
'''

VERSAO = '1.0.0'

from trataInviab import *
from inviab import *
from retiraInviab import *
import glob
from shutil import copyfile

from trataIntercambio import *

import sys
import numpy as np

import funcoes
import arrumaDadger

usinas_hidr = [0, 0, 0]  # foi necessario inicializar alguns itens da lista para que a insercao futura de atributos seja feita no lugar certo

# Importa Hidr
for i in range(1,320):
    usina = importaHidr.cUHE(i)
    usina.leHidr()
    usinas_hidr.insert(i,usina)

# primeiro verifica em qual versao do DECOMP esta trabalhando
# obtem o nome do arquivo
relato1 = glob.glob('relato.*')
try:
    # tenta abrir o arquivo
    with open(relato1[0], 'r', encoding="latin_1") as arqRelato:
        #pula 5 linhas
        linha = arqRelato.readline()
        linha = arqRelato.readline()
        linha = arqRelato.readline()
        linha = arqRelato.readline()
        linha = arqRelato.readline()
        versaoDecomp = linha[60:64].replace(".","")
        versaoDecomp = int(versaoDecomp.replace("-", ""))
        if(versaoDecomp < 100):
            versaoDecomp = versaoDecomp * 10

except :
    #se nao achou assume que eh a versao 27
    versaoDecomp = 270

# verifica em qual iteracao esta
# abre o arquivo iteracao.log
try:
    # tenta abrir o arquivo
    with open('iteracao.log', 'r', encoding="latin_1") as arqIteracao:
        linha = arqIteracao.readline()
        iteracao = int(linha[0:2])
except IOError:
    #se nao existe o arquivo eh a primeira iteracao
    iteracao = 1
    with open('iteracao.log', 'w', encoding="latin_1") as arqIteracao:
        arqIteracao.write('1')

#verifica se jah existe uma copia do dadger_original
# obtem o nome do arquivo
dadger = glob.glob('dadger.*')

#obtem a ultima etapa
ultima_etapa = arrumaDadger.arruma_cortes(dadger[0])

arrumaDadger.expande_dadger(dadger[0])

# abre o arquivo de log, para informar em qual iteracao esta
with open('retirainviab.log', 'a', encoding="latin_1") as arqRetInviab:
    # informa que esta na etapa de leitura das regras
    arqRetInviab.write('-------------------------------------------------------\n')
    arqRetInviab.write('INICIO DA ITERACAO: ' + str(iteracao) + '\n')

# cria a classe que faz a interface com as regras de flexibilizacao
regras = cRegras()
# primeiro verifica se o arquivo contendo as correspondencias (Inviabilidade x onde flexibiliar) encontra-se no diretorio
# carrega na memoria a lista de regras entre inviabilidade e onde flexibilizar
if not(regras.carregaRegraInviab()):
    exit()

# cria a classe que armazena as inviabilidades
inviab = cInviab()
# primeiro verifica se o arquivo contendo as inviabilidades encontra-se no diretorio
# carrega na memoria a lista de inviabilidade
if not(inviab.carregaInviab(versaoDecomp, usinas_hidr)):
    exit()

# verifica se o caso esta convergido
if len(inviab.listaTipo) > 0:

    # faz uma copia do dadger que acabou de rodar
    nome_explodido = dadger[0].split('.')
    copyfile(dadger[0], "dadger_" + str(iteracao) + "." + str(nome_explodido[-1]))

    # chama a funcao que vai retirar as inviabilidades
    if not(retiraInviab(inviab, regras, iteracao, usinas_hidr, ultima_etapa)):
        # abre o arquivo iteracao.log e muda a iteracao para 8888 (regra nao encontrada)
        with open('iteracao.log', 'w', encoding="latin_1") as arqIteracao:
            #arqIteracao.write('8888')
            arqIteracao.write(str(iteracao + 1))
    else:
        # abre o arquivo iteracao.log e incrementa a proxima iteracao
        with open('iteracao.log', 'w', encoding="latin_1") as arqIteracao:
            arqIteracao.write(str(iteracao + 1))

else:
    # chama a função que corrige o loop de intercâmbio ou a política indevida no Sul
    segue = trataIntercambio(iteracao)

    if segue:
        # abre o arquivo iteracao.log e incrementa a proxima iteracao
        with open('iteracao.log', 'w', encoding="latin_1") as arqIteracao:
            arqIteracao.write(str(iteracao + 1))
    else:
        # informa que o caso esta convergido
        # abre o arquivo iteracao.log e muda a iteracao para 9999 (caso convergido)
        with open('iteracao.log', 'w', encoding="latin_1") as arqIteracao:
                arqIteracao.write('9999')
