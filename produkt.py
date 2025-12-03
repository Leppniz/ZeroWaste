from datetime import datetime

class Produkt:
    def __init__(self, id, name, dataWaznosci, tagi=None, ilosc=0, jednostka="sztuk"):
        self._id = id
        self._name = name
        self._tagi = tagi if tagi is not None else []
        self._dataWaznosci = self._parse_date(dataWaznosci)
        self._ilosc = ilosc
        self._jednostka = jednostka

    # -------------------- Get
    def getId(self):
        return self._id

    def getName(self):
        return self._name

    def getDataWaznosci(self):
        return self._dataWaznosci

    def getTagi(self):
        return self._tagi

    def getIlosc(self):
        return self._ilosc

    def getJednostka(self):
        return self._jednostka

    # -------------------- Set
    def setName(self, new_name):
        self._name = new_name

    def setDataWaznosci(self, data):
        self._dataWaznosci = self._parse_date(data)

    def setTagi(self, tagi):
        self._tagi = tagi

    def setIlosc(self, ilosc):
        self._ilosc = ilosc

    def setJednostka(self, jednostka):
        self._jednostka = jednostka

    # -------------------- Tagi
    def addTag(self, tag):
        if tag not in self._tagi:
            self._tagi.append(tag)

    def removeTag(self, tag):
        if tag in self._tagi:
            self._tagi.remove(tag)

    # -------------------- Sprawdz date
    def isExpired(self):
        return datetime.now() > self._dataWaznosci


