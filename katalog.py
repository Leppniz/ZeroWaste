from typing import List
from produkt import Produkt
from settings import DAYS_TO_WARNING

class Katalog:
    def __init__(self):
        self._produkty: List[Produkt] = []

    def addProdukt(self, produkt: Produkt):
        self._produkty.append(produkt)

    def wyswietl(self):
        for p in self._produkty:
            print(p.getInfo())

    def getAll(self):
        return self._produkty

    def getProduktById(self, id_produktu):
        for p in self._produkty:
            if p.id == id_produktu:
                return p
        return None

    def removeProduktById(self, id_produktu):
        for p in self._produkty:
            if p.id == id_produktu:
                self._produkty.remove(p)
                return True
        return False

    # === METODY LOGIKI BIZNESOWEJ ===

    def count_all(self):
        return len(self._produkty)

    def count_expiring_soon(self):
        """Zwraca liczbę produktów, którym kończy się termin"""
        licznik = 0
        for p in self._produkty:
            dni = p.ile_dni_waznosci
            if dni is not None:
                if 0 <= dni <= DAYS_TO_WARNING:
                    licznik += 1
        return licznik

    def count_expired(self):
        """Zwraca liczbę przeterminowanych"""
        licznik = 0
        for p in self._produkty:
            dni = p.ile_dni_waznosci
            if dni is not None and dni < 0:
                licznik += 1
        return licznik

    def count_frozen(self):
        """Zwraca liczbę zamrożonych produktów"""
        licznik = 0
        for p in self._produkty:
            if p.isFrozen == True:
                licznik += 1
        return licznik

    def get_produkty_by_tag(self, tag: str):
        return [p for p in self._produkty if p.has_tag(tag)]
