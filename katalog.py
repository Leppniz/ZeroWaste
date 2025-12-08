class Katalog:
    def __init__(self):
        self._produkty = []

    def addProdukt(self, produkt):
        self._produkty.append(produkt)

    def displayAll(self):
        for p in self._produkty:
            print(p.getInfo())

    def getProductById(self, id_to_get):
        """"Zwraca obiekt produktu lub None, jeśli nie znaleziono"""
        for p in self._produkty:
            if p.id == id_to_get:
                return p
        return None

    def removeProductById(self, id):
        for p in self._produkty:
            if p.id == id:
                self._produkty.remove(p)
                return True
        return False

