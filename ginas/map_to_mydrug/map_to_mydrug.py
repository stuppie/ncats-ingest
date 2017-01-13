#!/usr/bin/env python3
"""
Parse fullSeedData-2016-06-16.json.gz file into a format suitable for mygene inport
Map to inchikeys, using fullSeedData-2016-06-16_UNII_wikidata.csv.gz'
Do mongo insert

"""


import pandas as pd
from collections import defaultdict
from pymongo import MongoClient
import json
import gzip
from biothings.utils.dataload import unlist

from local import MONGO_PASS


def unlist_collection(x):
    """ if x is len 1, return x[0]"""
    if isinstance(x, (list, tuple, set)) and len(x) == 1:
        return list(x)[0]
    else:
        return x


def parse_codes(d):
    """
    Convert a list of tuples of key-value pairs into a merged dict.
    example: [('a',5), ('a',6), ('b', 123)] -> {'a': [5, 6], 'b': 123}
    """
    dd = defaultdict(set)
    for k, v in d:
        dd[k].add(v)
    return unlist({k: list(v) for k, v in dd.items()})


def process_ginas_json(unii_inchikey):
    json_f = gzip.open("fullSeedData-2016-06-16.json.gz", 'rt', encoding='utf8')
    for line in json_f:
        d = json.loads(line)
        if d['substanceClass'] not in {'mixture', 'chemical'}:
            continue
        d['cas_primary'] = unlist_collection([x['code'] for x in d['codes'] if x['codeSystem'] == "CAS" and x['type'] == "PRIMARY"])
        d['preferred_name'] = unlist_collection([x['name'] for x in d['names'] if x['preferred']])
        d['names_list'] = [x['name'] for x in d['names']]
        d['xrefs'] = parse_codes([(x['codeSystem'], x['code']) for x in d['codes']])
        # some codes ('Food Contact Sustance Notif, (FCN No.)') have a period, which mongo doesn't like
        d['xrefs'] = {k.replace(".", "_"):v for k, v in d['xrefs'].items()}
        d['unii'] = d['approvalID']

        if d['substanceClass'] == 'mixture':
            d['mixture_unii'] = [x['substance']['approvalID'] for x in d['mixture']['components'] if
                                 x['type'] == "MUST_BE_PRESENT"]
            d['mixture_inchikey'] = [unii_inchikey.get(unii, None) for unii in d['mixture_unii']]

        inchikey = unii_inchikey.get(d['unii'], None)
        if inchikey:
            d['inchikey'] = inchikey
            yield {'_id': inchikey, 'ginas': d}
        else:
            yield {'_id': d['unii'], 'ginas': d}

if __name__ == "__main__":
    df = pd.read_csv('fullSeedData-2016-06-16_UNII_wikidata.csv.gz', index_col=0, low_memory=False)
    unii_inchikey = dict(zip(df.UNII, df.inchikey))
    unii_inchikey = {k:v for k,v in unii_inchikey.items() if pd.notnull(v)}

    dd = list(process_ginas_json(unii_inchikey))

    with open("ginas_dump.json", 'w') as f:
        json.dump(dd, f)

    db = MongoClient('mongodb://mydrug_user:{}@su08.scripps.edu:27017/drugdoc'.format(MONGO_PASS)).drugdoc
    coll = db.ginas
    coll.drop()
    coll.insert_many(dd)