class Katalog:
    def __init__(self):
        self._produkty = []


    def addProdukt(self, produkt):
        self._produkty.append(produkt)

    def removeProduktByName(self, name):
        for p in self._produkty:
            if p.getName() == name:
                self._produkty.remove(p)
                return True
        return False

