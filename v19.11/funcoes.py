import glob

class cDADGER():

    def __init__(self):
        self.pesada = 0
        self.media = 0
        self.leve = 0

    def obtemDuracaoPatamares(self):
        try:
            arquivo = glob.glob('dadger.*')
            with open(arquivo[0], 'r', encoding="latin_1") as arqDADGER:
                print(arqDADGER)
                for line in arqDADGER:
                    if "DP   1    1   3" in line[0:15]:
                        self.pesada = float(line[35:40])
                        self.media = float(line[55:60])
                        self.leve = float(line[75:80])
                        self.total = self.pesada + self.media + self.leve
        except IOError:
            print('Arquivo DADGER.* nao encontrado')