from typing import List
from produkt import Produkt
from settings import DAYS_TO_WARNING
from datetime import datetime

class Katalog:
    def __init__(self):
        self._produkty: List[Produkt] = []

    def addProdukt(self, nowy_produkt):
        for p in self._produkty:
            zgodna_nazwa = p.name.strip().lower() == nowy_produkt.name.strip().lower()
            zgodna_data = p.data_waznosci == nowy_produkt.data_waznosci
            zgodna_jednostka = getattr(p, 'jednostka', 'szt') == getattr(nowy_produkt, 'jednostka', 'szt')
            zgodne_mrozenie = p.isFrozen == nowy_produkt.isFrozen

            if zgodna_nazwa and zgodna_data and zgodna_jednostka and zgodne_mrozenie:
                p.ilosc += nowy_produkt.ilosc
                return

        self._produkty.append(nowy_produkt)

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

    def get_grouped_by_name(self):
        grupa = {}

        for p in self._produkty:
            nazwa_ladna = p.name.strip().capitalize()
            # Pobieramy jednostkę bezpiecznie
            jednostka = getattr(p, 'jednostka', 'szt')

            # TWORZYMY KLUCZ UNIKALNY: (Nazwa, Jednostka)
            # Dzięki temu "Mleko (l)" i "Mleko (szt)" to będą dwie osobne pozycje!
            klucz = (nazwa_ladna, jednostka)

            if klucz not in grupa:
                grupa[klucz] = 0.0  # Startujemy od zera (float)

            grupa[klucz] += p.ilosc

        return grupa

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

    def podmienProdukt(self, id_produktu, nowy_obiekt):
        # Szukamy, na którym miejscu w liście (index) leży stary produkt
        for i, p in enumerate(self._produkty):  # lub self.produkty zależnie jak nazwałeś listę
            if p.id == id_produktu:
                # Znaleziono! Podmieniamy stary na nowy
                self._produkty[i] = nowy_obiekt
                return True
        return False

    #  Znajdowanie duplikatów
    def znajdzDuplikat(self, nazwa, data_str, jednostka, is_frozen, id_wykluczone):
        """
        Szuka produktu o identycznych parametrach, ale innym ID.
        Zwraca znaleziony obiekt produktu lub None.
        """
        try:
            szukana_data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            # Jeśli data jest pusta lub błędna, szukamy None
            szukana_data = None

        for p in self._produkty:
            # Nie sprawdzamy produktu, który właśnie edytujemy!
            if p.id == id_wykluczone:
                continue

            zgodna_nazwa = p.name.strip().lower() == nazwa.strip().lower()

            zgodna_data = p.data_waznosci == szukana_data

            p_jednostka = getattr(p, 'jednostka', 'szt')
            zgodna_jednostka = p_jednostka == jednostka

            zgodne_mrozenie = p.isFrozen == is_frozen

            if zgodna_nazwa and zgodna_data and zgodna_jednostka and zgodne_mrozenie:
                return p

        return None