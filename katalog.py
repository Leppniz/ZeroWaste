class Katalog:
    def __init__(self):
        self._produkty = []

    def addProdukt(self, produkt):
        self._produkty.append(produkt)

    def wyswietl(self):
        for p in self._produkty:
            print(p.getInfo())

    # Zmiana na usuwanie po id żeby przypadkiem nie
    # wywalić wszystkich o tych samych nazwach
def removeProduktById(self, id):
        for p in self._produkty:
            if p.getId() == id:
                self._produkty.remove(p)
                return True
        return False

