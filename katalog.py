class Katalog:
    def __init__(self):
        self._produkty = []

    def addProdukt(self, produkt):
        self._produkty.append(produkt)

    def wyswietl(self):
        for p in self._produkty:
            print(p.getInfo())

    def getAll(self):
        return self._produkty

    def removeProduktById(self, id_produktu):
        for p in self._produkty:
            if p.id == id_produktu:
                self._produkty.remove(p)
                return True
        return False