


class VnUriFrag:
    def __init__(self, unhyphen=False):
        self.unhyphen = unhyphen
    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name, None)
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        _val = str(value).replace(" ","").upper()
        if self.unhyphen:
            _val = _val.replace("-","")
        instance.__dict__["_"+self.name] = _val
    def __set_name__(self, owner, name):
        self.name = name    


class VnUri:
    country = VnUriFrag(unhyphen=True)
    field = VnUriFrag(unhyphen=True)
    tag = VnUriFrag(unhyphen=True)
    subtag = VnUriFrag(unhyphen=True)

    def __init__(self, country, field, tag, subtag=None):
        self.country = country
        self.field = field
        self.tag = tag
        if subtag:
            self.subtag = subtag
        self.sep1 = "|"
        self.sep2 = ":"
        self.make_uri()


    def make_uri(self):
        self.make_ast_uri()

    def make_ast_uri(self):
        ast_uri = f"{self._country}{self.sep2}{self._field}{self.sep2}{self._tag}"
        if self.subtag:
            ast_uri +=  f"{self.sep2}{self._subtag}"
        self.ast_uri = ast_uri
        self.ast_uri_fname = self.uri_to_fname(ast_uri)
        return ast_uri

    @staticmethod
    def uri_to_fname(uri):
        # https://docs.python.org/3/library/stdtypes.html#str.maketrans
        tt_map = {" ":"", "|":"__", ":":"--"}
        tt = str.maketrans(tt_map)
        fname = uri.translate(tt)
        return fname


if __name__ == "__main__":
    v1 = VnUri("NOR", "Skarv", "subsea")
