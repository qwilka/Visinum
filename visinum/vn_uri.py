import hashlib
import re

import dateutil.parser  # https://stackoverflow.com/questions/23385003/attributeerror-when-using-import-dateutil-and-dateutil-parser-parse-but-no


def vn_uri_to_filename(vn_uri):
    # uriFname = uri
    # uriFname = uriFname.replace(" ", "")
    # uriFname = uriFname.replace("-", "")
    # uriFname = uriFname.replace("_", "")
    # uriFname = uriFname.replace("|", "_")
    # uriFname = uriFname.replace(":", "-")
    # https://docs.python.org/3/library/stdtypes.html#str.maketrans
    tt_map = {" ":"", "-":"", "_":"", "|":"_", ":":"-"}
    tt = str.maketrans(tt_map)
    # filename = vn_uri.translate(str.maketrans(tt))
    # preserve minus sign - in loc_URI
    uricomps = vn_uri.split("|")
    for ii, _comp in enumerate(uricomps):
        if ii==1 and any(ss in _comp for ss in ("E", "KP", "LG", "BB")):
            uricomps[ii] = _comp.replace(":", "-")
            continue
        uricomps[ii] = _comp.translate(tt)
    filename = "_".join(uricomps)
    return filename


def string2hash(ss):
    _hash = hashlib.md5(ss.encode()).hexdigest()
    return _hash


def make_ast_URI(country, field, domain, subdomain=""):
    """identifier "country:field:domain" 
    country is 3-letter code ISO_3166-1_alpha-3 https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
    (For 2-letter codes refer to ISO_3166-1_alpha-2 )
    field in uppercase
    """
    if country.upper() in ["DENMARK","DK","DNK"]:
        country = "DNK"
    elif country.upper() in ["FRANCE","FR","FRA"]:
        country = "FRA"
    elif country.upper().replace(" ","") in ["UNITEDKINGDOM","GREATBRITAIN","BRITAIN","UK","GB","GBR"]:
        country = "GBR"
    elif country.upper() in ["IRELAND","EIRE","IE","IRL"]:
        country = "IRL"
    if country.upper() in ["NORWAY","NO","NOR"]:
        country = "NOR"
    elif country.upper().replace(" ","").replace("OF","") in ["UNITEDSTATES","UNITEDSTATESAMERICA","US","USA"]:
        country = "USA"
    field = field.upper().replace(" ","")
    domain = domain.upper().replace(" ","")
    ast_URI = f"{country}:{field}:{domain}"
    if subdomain:
        ast_URI = f"{ast_URI}:{subdomain}"
    return ast_URI


def make_loc_URI(long=None, lat=None, bbox=None, E=None, N=None,
        KP1=None, KP2=None):
    if long is not None and lat is not None:
        return f"LG{long}:LT{lat}"
    elif E is not None and N is not None:
        return f"E{E}:N{N}"
    elif bbox and isinstance(bbox, (list, tuple)):
        return "BB" + ":".join(map(lambda x: str(x), bbox))
    elif KP1 is not None:
        _uri = f"KP{KP1}"
        if KP2 is not None:
            _uri = f"{_uri}:KP{KP2}"
        return _uri
    else:
        return None


def make_vn_date(vn_date):
    _vn_date = vn_date.strip()
    _date = dateutil.parser.isoparse(_vn_date)
    _date = _date.date().isoformat()
    # dateutil.parser appends "-01-01" if DD or MM omitted
    #if _date.endswith("-01-01"):
    if re.search(r"-(0[1-9]|1[0-2])-01$", _date):
        #if _vn_date.endswith("-01-01"):
        if re.search(r"-(0[1-9]|1[0-2])-01$", _vn_date):
            pass
        #elif _vn_date.endswith("-01"):
        elif re.search(r"-(0[1-9]|1[0-2])$", _vn_date):
            _date = _date[:-3]
        else:
            _date = _date[:-6]
    return _date


def make_vn_URI(vn_ast="", country="", field="", domain="", subdomain="",
    vn_loc=None, long=None, lat=None, bbox=None, E=None, N=None, KP1=None, KP2=None,
    date1=None, date2=None,
    vn_cat=None, return_dict=False):
    if not vn_ast:
        vn_ast = make_ast_URI(country, field, domain, subdomain)
        _uri = f"{vn_ast}"
    if not vn_loc:
        vn_loc = make_loc_URI(long, lat, bbox, E, N, KP1, KP2)
    if vn_loc:
        _uri = f"{_uri}|{vn_loc}"
    if date1:
        # _d1 = dateutil.parser.isoparse(date1)
        # _d1 = _d1.date().isoformat()
        vn_date = make_vn_date(date1)
        if date2: # for date range...
            # _d2 = dateutil.parser.isoparse(date2)
            # _d2 = _d2.date().isoformat()
            _d2 = make_vn_date(date2)
            vn_date = f"{vn_date}:{_d2}"
        _uri = f"{_uri}|{vn_date}"
    if vn_cat:
        # ?test valid vn_cat
        _uri = f"{_uri}|{vn_cat}"
    if return_dict:
        return {
            "vn_uri": _uri,
            "vn_ast": vn_ast,
            "vn_loc": vn_loc,
            "vn_date": vn_date,
            "vn_cat": vn_cat,
        }
    else:
        return _uri
