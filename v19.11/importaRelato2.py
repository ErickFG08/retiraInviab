# -*- coding: latin-1 -*-

import sys
import glob

class c_relato2:

    def __init__(self):

        Qtur_usina = []
        geracao_media = []
        produtibilidade = []

        num_cenarios = 0

    def leRelato2(self, relato_entrada, usina, cenario):

        dadger = glob.glob('dadger.*')

        try:

            with open(dadger[0], 'r') as dadger_:

               for line in dadger_:

                    if '& ESTRUTURA DA ARVORE               =>' in line:

                        num_cenarios = int(line[39:42]) + 1

            dadger_.close()

        except:

            sys.exit('Dadger nao encontrado')

        linha_cenario = []
        linha_inicial = []
        linha_final = []

        # Importa vazao turbinavel

        try:

            with open(relato_entrada, 'r') as relato:

                linhas = relato.readlines()

        except:

            sys.exit('Relato2 nao encontrado')

        with open(relato_entrada, 'r') as relato:

            num1 = 0
            num2 = 0

            for line in relato:

                if 'RELATORIO  DO  BALANCO  HIDRAULICO' in line:

                    num_linha_cenario = num1 + 2

                    i = 0

                    linha_cenario = linhas[num_linha_cenario]

                    if int(linha_cenario[48:51].strip()) == cenario:

                        linha_inicial = num1 + 8

                        i = 1

                elif 'Relatorio das Restricoes Hidraulicas  de Vazao Afluente (m3/s)' in line and i == 1:

                    linha_final = num2 - 2

                    exit

                num1 += 1
                num2 += 1

            pass        
            
        with open(relato_entrada, 'r') as relato:

            linhas = relato.readlines()

            for i in range(linha_inicial, linha_final):

                linha = linhas[i]

                if linha[4:16].strip() == usina.strip():

                    Qtur_usina = (float(linha[37:43].strip()))

        # Importa geracao termica

        with open(relato_entrada, 'r') as relato:

            num1 = 0
            num2 = 0

            for line in relato:

                if 'Ini.  Fin.  Esp.   Qnat   (  %MLT)   Qafl     Qdef    GER_1   GER_2   GER_3    Media   VT(*)   VNT    Ponta   FPCGC' in line:

                    num_linha_cenario = num1 - 8

                    linha_cenario = linhas[num_linha_cenario]

                    i = 0

                    if int(linha_cenario[48:51].strip()) == cenario:

                        linha_inicial = num1 + 2

                        i = 1

                elif '(*) OBS.: os valores da energia vertida turbinavel contem os desvios da funcao de producao' in line and i == 1:

                    linha_final = num2 - 11

                    exit

                num1 += 1
                num2 += 1

            pass

        with open(relato_entrada, 'r') as relato:

            linhas = relato.readlines()

            for i in range(linha_inicial, linha_final):

                linha = linhas[i]

                if linha[9:21].strip() == usina.strip():

                    geracao_media = (float(linha[105:111].strip()))

                    produtibilidade = (geracao_media/Qtur_usina)

        return produtibilidade
