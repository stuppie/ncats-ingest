#!/usr/bin/env python3
"""
Create summary cvs of external IDs from fullSeedData-2016-06-16.gsrs file
Expects one json doc per line
created like:
cut -f3- fullSeedData-2016-06-16.gsrs > fullSeedData-2016-06-16_cut.json

usage: summarize_gsrs.py fullSeedData-2016-06-16_cut.json outfile.csv

"""


import json
import sys
from collections import defaultdict

import pandas as pd


def parse_codes(d):
    dd = defaultdict(set)
    for k, v in d:
        dd[k].add(v)
    return {k: '|'.join(v) for k, v in dd.items()}


def to_pandas(f):
    codes = {}
    for line in f:
        doc = json.loads(line)
        uuid = doc['uuid']
        codes[uuid] = parse_codes([(x['codeSystem'], x['code']) for x in doc['codes']])
        codes[uuid]['CAS_primary'] = "|".join([x['code'] for x in doc['codes'] if x['codeSystem'] == "CAS" and x['type'] == "PRIMARY"])
        codes[uuid]['UNII'] = doc.get('approvalID', None)
        codes[uuid]['substanceClass'] = doc['substanceClass']
        codes[uuid]['names'] = '|'.join([x['name'] for x in doc['names']])
        codes[uuid]['preferred_names'] = '|'.join([x['name'] for x in doc['names'] if x['preferred']])

        # TODO for mixture extract componenets
        # ANTIBIOTIC A-40926
        if "mixture" in doc and "components" in doc['mixture']:
            codes[uuid]['mixture_UNII'] = "|".join([x['substance']['approvalID'] for x in doc['mixture']['components'] if x['type'] == "MUST_BE_PRESENT"])
        else:
            codes[uuid]['mixture_UNII'] = None

    df = pd.DataFrame(codes).T
    df['uuid'] = df.index
    return df

if __name__ == "__main__":
    f = open(sys.argv[1])
    df = to_pandas(f)

    # only keep chemicals and mixtures
    df = df[df.substanceClass.isin({'chemical','mixture'})]
    # toss columns that don't have at least 100 values (out of ~86k)
    df = df[df.columns[df.count() > 100]]
    # must have a CAS number
    # this gets rid of food and stuff like "STONE CRAB"
    df = df[~df.CAS.isnull()]

    df.to_csv(sys.argv[2])
    print(df.count())

