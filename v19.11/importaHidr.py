# -*- coding: latin-1 -*-

import sys
import numpy as np

class cUHE:
    
    def __init__(self,numUsina,nper=60):

        self.numero = numUsina
        self.nome = ''
        self.posto = 0
        self.jusante = 0
        self.REE = 0
        self.status = ''
        self.flagModif = 0
        self.AnoInicialHist = 0
        self.AnoFinalHist = 0

        self.volMin = 0
        self.volMax = 0
        self.cotaMin = 0
        self.cotaMax = 0
        self.PCV = np.zeros(5)
        self.PCA = np.zeros(5)
        self.evaporacao = np.zeros(12)
        self.numConjMaq = 0
        self.numMaqCnj = np.zeros(5)
        self.potencia = np.zeros(5)
        self.hEf = np.zeros(5)
        self.qEf = np.zeros(5)
        self.prodt = 0
        self.perdas = 0
        self.cotaCFuga = 0
        self.fcMax = 0
        self.vazaoMin = 0
        self.numBas = 0
        self.tipoTurb = 0
        self.teif = 0
        self.ip = 0
        self.tipoPerda = 0
        self.volRef = 0
        self.tipoRegul = ''

        self.vazaoMinTempo = np.zeros(nper)
        self.volMaxOperativo = np.zeros(nper)
        self.volMinOperativo = np.zeros(nper)
        self.cotaCFugaVariavel = np.zeros(nper)
        self.numMaqCnjExpansao = np.zeros((nper,5))

    def leHidr(self, NomeArq='hidr.dat'):

        try:

            with open(NomeArq, 'r') as hidr:

                pass
        except:

            sys.exit('Arquivo %s não encontrado' % NomeArq)

        with open(NomeArq, 'rb') as hidr:

            hidr.seek((self.numero - 1) * 792)
            self.nome = np.fromfile(hidr, dtype=np.int8, count=12).tobytes().decode(encoding='utf_8')  # Nome
            self.posto = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Posto
            dummy = np.fromfile(hidr, dtype=np.int8, count=8)[0]  # Posto BDH
            dummy = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Subsistema
            dummy = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Empresa
            dummy = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Jusante
            dummy = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Desvio
            self.volMin = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Vol Min
            self.volMax = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Vol Máx
            self.volUtil = self.volMax - self.volMin
            dummy = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Vol Vertedouro
            dummy = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Vol Crista Desvio
            self.cotaMin = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Cota Mínima
            self.cotaMax = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Cota Máxima
            self.PCV = np.fromfile(hidr, dtype=np.float32, count=5)  # PCV
            self.PCA = np.fromfile(hidr, dtype=np.float32, count=5)  # PCA
            self.evaporacao = np.fromfile(hidr, dtype=np.int32, count=12)  # Evaporação
            self.numConjMaq = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Num. Conjunto Máquinas
            self.numMaqCnj = np.fromfile(hidr, dtype=np.int32, count=5)  # Num. Maq Conjunto
            self.potencia = np.fromfile(hidr, dtype=np.float32, count=5)  # Potência do Conjunto
            for i in range(5):  np.fromfile(hidr, dtype=np.float32, count=5)  # ???
            for i in range(5):  np.fromfile(hidr, dtype=np.float32, count=5)  # ???
            for i in range(5):  np.fromfile(hidr, dtype=np.float32, count=5)  # ???
            self.hEf = np.fromfile(hidr, dtype=np.float32, count=5)  # Altura queda nominal
            self.qEf = np.fromfile(hidr, dtype=np.int32, count=5)  # Vazão nominal
            self.prodt = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Produtibilidade específica
            self.perdas = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Perdas
            np.fromfile(hidr, dtype=np.int32, count=1)  # Número polinomios jusante

            for i in range(6):

                np.fromfile(hidr, dtype=np.float32, count=5)  # Polinômios jusante

            np.fromfile(hidr, dtype=np.float32, count=6)  # Referência Pol. Jusante
            self.cotaCFuga = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Canal de Fuga
            dummy = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Influência Vertimento CFuga
            self.fcMax = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Fator Carga Máximo
            dummy = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Fator Carga Mínimo
            self.vazaoMin = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Vazão mínima
            self.numBas = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Número unidades base
            self.tipoTurb = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Tipo turbina
            dummy = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Representação do conjunto
            self.teif = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Taxa indisp. forçada
            self.ip = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Taxa indisp. programada
            self.tipoPerda = np.fromfile(hidr, dtype=np.int32, count=1)[0]  # Tipo Perda
            dummy = np.fromfile(hidr, dtype=np.int8, count=8).tobytes().decode(encoding='utf_8')  # Data
            dummy = np.fromfile(hidr, dtype=np.int8, count=43).tobytes().decode(encoding='utf_8')  # Obs
            self.volRef = np.fromfile(hidr, dtype=np.float32, count=1)[0]  # Vol referência
            self.tipoRegul = np.fromfile(hidr, dtype=np.int8, count=1).tobytes().decode(encoding='utf_8')  # Tipo regul.

    def inicializaVarTempo(self,mesi=1):

        self.vazaoMinTempo[mesi-1] = self.vazaoMin
        self.volMaxOperativo[mesi-1] = self.volMax
        self.volMinOperativo[mesi-1] = self.volMin
        self.cotaCFugaVariavel[mesi-1] = self.cotaCFuga

        for i in range(5):
            
            self.numMaqCnjExpansao[mesi-1,i] = self.numMaqCnj[i]




