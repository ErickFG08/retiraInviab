# -*- coding: latin-1 -*-

# # # Funcao para arrumar o arquivo dadger

import glob, os

def arruma_cortes(arquivo_dadger):

    name, ext = os.path.splitext(arquivo_dadger)

    fin = open(arquivo_dadger, 'r+', encoding = "latin_1")

    fout = open(arquivo_dadger + "_" + ext, 'w+', encoding = "latin_1")

    for linha1 in fin:

        if 'CORTESH.P0' in linha1:

            fout.write('FC  NEWV21    cortesh.dat\n')

        elif 'CORTES.P0' in linha1:
            
            fout.write('FC  NEWV21    cortes.dat\n')

        elif 'DP  ' in linha1:

            ultima_etapa = int(linha1[5:6])

            fout.write(linha1)

        else:
            
            fout.write(linha1)

    fin.close()

    fout.close()

    os.remove(arquivo_dadger)

    os.rename(arquivo_dadger + "_" + ext, arquivo_dadger)

    return ultima_etapa

def inverte_arquivo(arquivo_entrada):

    name, ext = os.path.splitext(arquivo_entrada)

    fin = open(arquivo_entrada, 'r+', encoding = "latin_1")

    fout = open(arquivo_entrada + "_" + ext, 'w+', encoding = "latin_1")

    linhas = fin.readlines()

    for linha1 in reversed(linhas):

        fout.write(linha1)

    fin.close()

    fout.close()

    os.remove(arquivo_entrada)

    os.rename(arquivo_entrada + "_" + ext, arquivo_entrada)

def expande_dadger(arquivo_dadger):

    name, ext = os.path.splitext(arquivo_dadger)

    fin = open(arquivo_dadger, 'r+', encoding = "latin_1")

    fout = open(arquivo_dadger + "_" + ext, 'w+', encoding = "latin_1")

    for linha1 in fin:

        if linha1[0:2] == 'RE' or linha1[0:2] == 'HQ' or linha1[0:2] == 'HV':

            fout.write(linha1)

            ultima_etapa_restricao = int(linha1[15:16])

        elif linha1[0:2] == 'LU' or linha1[0:2] == 'LQ' or linha1[0:2] == 'LV':

            fout.write(linha1)

            while int(linha1[10:11]) < ultima_etapa_restricao:

                linha_nova = linha1[0:9] + ' ' + str(int(linha1[10:11]) + 1) + ' ' + linha1[12:len(linha1)-1] + '\n'

                fout.write(linha_nova)

                linha1 = linha_nova

        else:

            fout.write(linha1)
    
    fin.close()

    fout.close()

    inverte_arquivo(arquivo_dadger + "_" + ext)

    fin = open(arquivo_dadger + "_" + ext, 'r+', encoding = "latin_1")

    fout = open(arquivo_dadger + "__" + ext, 'w+', encoding = "latin_1")

    etapa_anterior = 0

    for linha1 in fin:

        if linha1[0:2] == 'LU' or linha1[0:2] == 'LQ' or linha1[0:2] == 'LV':

            etapa_atual = int(linha1[10:11])

            if etapa_anterior == 0:

                fout.write(linha1)

                etapa_anterior = etapa_atual

            else:

                if etapa_atual < etapa_anterior:

                    fout.write(linha1)

                    etapa_anterior = etapa_atual
        else:

            fout.write(linha1)

            etapa_anterior = 0

    fin.close()

    fout.close()

    inverte_arquivo(arquivo_dadger + "__" + ext)

    os.remove(arquivo_dadger)

    os.remove(arquivo_dadger + "_" + ext)

    os.rename(arquivo_dadger + "__" + ext, arquivo_dadger)

def retrai_dadger(arquivo_dadger):

    name, ext = os.path.splitext(arquivo_dadger)

    fin = open(arquivo_dadger, 'r+', encoding = "latin_1")

    fout = open(arquivo_dadger + "_" + ext, 'w+', encoding = "latin_1")

    primeira_parte_etapa_anterior = ""

    etapa_anterior = 0

    ultima_parte_etapa_anterior = ""

    for linha1 in fin:

        if linha1[0:2] == 'LU' or linha1[0:2] == 'LQ' or linha1[0:2] == 'LV':

            primeira_parte_etapa_atual = linha1[0:9]

            etapa_atual = int(linha1[10:11])

            ultima_parte_etapa_atual = linha1[12:len(linha1)-1]

            if primeira_parte_etapa_anterior == "" and etapa_anterior == 0 and ultima_parte_etapa_anterior == "":

                fout.write(linha1)

            elif primeira_parte_etapa_atual == primeira_parte_etapa_anterior and etapa_atual == etapa_anterior + 1 and ultima_parte_etapa_anterior != ultima_parte_etapa_atual:

                fout.write(linha1)

            primeira_parte_etapa_anterior = linha1[0:9]

            etapa_anterior = int(linha1[10:11])

            ultima_parte_etapa_anterior = linha1[12:len(linha1)-1]

        else:

            fout.write(linha1)

            primeira_parte_etapa_anterior = ""

            etapa_anterior = 0

            ultima_parte_etapa_anterior = ""

    fin.close()

    fout.close()

    os.rename(arquivo_dadger + "_" + ext, arquivo_dadger)

    os.remove(arquivo_dadger + "_" + ext)