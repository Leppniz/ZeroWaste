from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import uuid

# Abstrakcja - robi taki szablon ze wszystko co korzysta z tego ma te dane
class Produkt(ABC):
    def __init__(self, name, data_waznosci=None):
        self._id = str(uuid.uuid4().hex)[:8]
        self._name = name
        self._data_waznosci = None
        self._isFrozen = False
        self._frozenDays = 64

        self.data_waznosci = data_waznosci

    # ENKAPSULACJA (Gettery i Settery)
    @property
    def id(self):
        return self._id

    @property
    def isFrozen(self):
        return self._isFrozen

    @isFrozen.setter
    def isFrozen(self, wartosc):
        if isinstance(wartosc, bool):
            self._isFrozen = wartosc
        else:
            print("Błąd: isFrozen musi być True lub False")

    @property
    def ile_dni_waznosci(self):
        """Zwraca liczbe dni do końca ważności lub None"""

        if self._data_waznosci is None:
            return None

        dataWaznosci = self._data_waznosci

        if self._isFrozen:
            dataWaznosci += timedelta(days=self._frozenDays)

        dzis = datetime.now().date()
        delta = dataWaznosci - dzis

        return delta.days

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, nowa_nazwa):
        if not nowa_nazwa:
            print("Błąd: Nazwa nie może być pusta!")
        else:
            self._name = nowa_nazwa

    @property
    def data_waznosci(self):
        if not self._isFrozen:
            return self._data_waznosci
        else:
            return self._data_waznosci + timedelta(days=self._frozenDays)

    @data_waznosci.setter
    def data_waznosci(self, nowa_data):
        if nowa_data is None:
            self._data_waznosci = None
            return

        if isinstance(nowa_data, str):
            try:
                self._data_waznosci = datetime.strptime(nowa_data, "%Y-%m-%d").date()
            except ValueError:
                print(f"Błąd: Zły foramt daty '{nowa_data}'. Użyj YYYY-MM-DD")
        elif isinstance(nowa_data, datetime) or isinstance(nowa_data, datetime.date):
            self._data_waznosci = nowa_data

    @abstractmethod
    def getInfo(self):
        pass

class ProduktSztuki(Produkt):
    def __init__(self, name, data_waznosci=None, ilosc=0):
        super().__init__(name, data_waznosci)
        self._ilosc = ilosc

    @property
    def jednostka(self):
        return "szt"

    @property
    def ilosc(self):
        return self._ilosc

    @ilosc.setter
    def ilosc(self, nowa_ilosc):
        if nowa_ilosc < 0:
            print("Błąd: Ilość sztuk nie może być ujemna!")
        else:
            self._ilosc = nowa_ilosc

    def getInfo(self):
        data_str = str(self.data_waznosci) if self._data_waznosci else "Brak daty"
        return f"[ID: {self._id}] {self._name}: {self._ilosc} szt. (Ważne do: {data_str} {self.ile_dni_waznosci} dni)"

class ProduktWaga(Produkt):
    def __init__(self, name, data_waznosci=None, ilosc=0.0, jednostka="kg"):
        super().__init__(name, data_waznosci)
        self._ilosc = ilosc
        self._jednostka = None

        self.jednostka = jednostka

    @property
    def jednostka(self):
        return self._jednostka

    @jednostka.setter
    def jednostka(self, nowa_jednostka):
        if nowa_jednostka in ['kg','g','l','ml']:
            self._jednostka = nowa_jednostka
        else:
            raise ValueError(f"Błąd krytyczny! '{nowa_jednostka}' to niedozwolona jednostka!")
    @property
    def ilosc(self):
        return self._ilosc

    @ilosc.setter
    def ilosc(self, nowa_ilosc):
        if nowa_ilosc < 0:
            print("Błąd: Waga nie może być ujemna!")
        else:
            self._ilosc = float(nowa_ilosc)

    def getInfo(self):
        data_str = str(self._data_waznosci) if self._data_waznosci else "Brak daty"
        return f"[ID: {self._id}] {self._name}: {self._ilosc} {self.jednostka} (Ważne do: {data_str} {self.ile_dni_waznosci} dni)"