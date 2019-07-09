import calendar
from datetime import datetime

from dataclasses import dataclass, replace
from parse import parse




@dataclass 
class VnUri: 
    country: str 
    field: str 
    tag: str 
    subtag: str = None
    date1: str = None
    date2: str = None

    def __post_init__(self):
        self._country =  self.norm(self.country)
        self._field =  self.norm(self.field)
        self._tag =  self.norm(self.tag)
        self.ast_uri = f"{self._country}:{self._field}:{self._tag}"
        if self.subtag:
            self._subtag = self.norm(self.subtag)
            self.ast_uri = f"{self.ast_uri}:{self._subtag}"
        if self.date1:
            self.make_date_uri()

    def make_date_uri(self):
        mat = parse("{datet:ti}", self.date1)
        if mat:
            self._dt1 = mat["datet"]
            self._dt2 = self._dt1
            self._date1 = self._dt1.strftime("%Y%m%d")
        else:
            mat = parse("{yr:d}-{mn:d}-{dy:d}", self.date1)
            if mat:
                self._dt1 = datetime(year=mat["yr"], month=mat["mn"], day=mat["dy"])
                self._dt2 = self._dt1
                self._date1 = self._dt1.strftime("%Y%m%d")
            else:
                mat = parse("{yr:d}-{mn:d}", self.date1)
                if mat:
                    self._dt1 = datetime(year=mat["yr"], month=mat["mn"], day=1)
                    _cr = calendar.monthrange(mat["yr"], mat["mn"])
                    self._dt2 = datetime(year=mat["yr"], month=mat["mn"], day=_cr[1])
                    self._date1 = self._dt1.strftime("%Y%m")
                else:
                    mat = parse("{yr:d}", self.date1)
                    if mat:
                        self._dt1 = datetime(year=mat["yr"], month=1, day=1)
                        self._dt2 = datetime(year=mat["yr"], month=12, day=31)
                        self._date1 = self._dt1.strftime("%Y")
        self.date_uri = self._date1
        if self.date2:
            mat = parse("{datet:ti}", self.date2)
            if mat:
                self._dt2 = mat["datet"]
                self._date2 = self._dt2.strftime("%Y%m%d")
            else:
                mat = parse("{yr:d}-{mn:d}-{dy:d}", self.date2)
                if mat:
                    self._dt2 = datetime(year=mat["yr"], month=mat["mn"], day=mat["dy"])
                    self._date2 = self._dt2.strftime("%Y%m%d")
                else:
                    mat = parse("{yr:d}-{mn:d}", self.date2)
                    if mat:
                        _cr = calendar.monthrange(mat["yr"], mat["mn"])
                        self._dt2 = datetime(year=mat["yr"], month=mat["mn"], day=_cr[1])
                        self._date2 = self._dt2.strftime("%Y%m")
                    else:
                        mat = parse("{yr:d}", self.date2)
                        if mat:
                            self._dt2 = datetime(year=mat["yr"], month=12, day=31)
                            self._date2 = self._dt2.strftime("%Y")
            self.date_uri = f"{self.date_uri}:{self._date2}"




    @staticmethod
    def norm(stg):
        return stg.replace(" ","").replace("-","").upper()

    @staticmethod
    def uri_to_fname(uri):
        # https://docs.python.org/3/library/stdtypes.html#str.maketrans
        tt_map = {" ":"", "|":"__", ":":"--"}
        tt = str.maketrans(tt_map)
        fname = uri.translate(tt)
        return fname


if __name__ == "__main__":
    v1 = VnUri("NOR", "Skarv", "sub sea ")
    v2 = replace(v1, country="irl", tag="18-F-101")
    v3 = VnUri("NOR", "Skarv", "subsea", date1="2001")
    v4 = replace(v3, subtag="32-F-0800")