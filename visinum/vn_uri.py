import calendar
from datetime import datetime
import hashlib

from dataclasses import dataclass, replace
from parse import parse



def string2hash(ss):
    _hash = hashlib.md5(ss.encode()).hexdigest()
    return _hash


@dataclass 
class VnUri: 
    country: str 
    field: str 
    tag: str 
    subtag: str = None
    date1: str = None
    date2: str = None
    KP1: str = None
    KP2: str = None
    vn_cat: str = None

    @property
    def _country(self):
        return self.norm(self.country)

    @property
    def _field(self):
        return self.norm(self.field)

    @property
    def _tag(self):
        return self.norm(self.tag)

    @property
    def _subtag(self):
        return self.norm(self.subtag)

    @property
    def vn_uri(self):
        _uri = self.ast_uri
        _date_uri = self.date_uri
        if _date_uri:
            _uri = f"{_uri}|{_date_uri}"
        _loc_uri = self.loc_uri
        if _loc_uri:
            _uri = f"{_uri}|{_loc_uri}"
        if self.vn_cat:
            _uri = f"{_uri}|{self.vn_cat}"
        return _uri

    @property
    def ast_uri(self):
        _uri = f"{self._country}:{self._field}:{self._tag}"
        if self.subtag:
            _uri = f"{_uri}:{self._subtag}"
        return _uri

    @property
    def date_uri(self):
        _uri = None
        if self.date1:
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
            _uri = self._date1
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
            _uri = f"{_uri}:{self._date2}"
        return _uri

    @property
    def loc_uri(self):
        #print("make_loc_uri:", self.KP1)
        _uri = None
        if self.KP1 is not None:
            _uri = f"KP{self.KP1}"
        if self.KP2 is not None:
            _uri = f"{_uri}:KP{self.KP2}"
        return _uri

    @property
    def ast_fname(self):
        return self.uri_to_fname(self.ast_uri)

    @property
    def vn_fname(self):
        return self.uri_to_fname(self.vn_uri)

    @staticmethod
    def norm(stg):
        if isinstance(stg, str):
            return stg.replace(" ","").replace("-","").upper()
        else:
            return None

    @staticmethod
    def uri_to_fname(uri):
        # https://docs.python.org/3/library/stdtypes.html#str.maketrans
        tt_map = {" ":"", "|":"__", ":":"--"}
        tt = str.maketrans(tt_map)
        fname = uri.translate(tt)
        return fname



