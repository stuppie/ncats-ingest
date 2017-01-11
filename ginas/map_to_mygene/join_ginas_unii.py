#!/usr/bin/env python3

import pandas as pd

ginas = pd.read_csv('fullSeedData-2016-06-16.csv', index_col=0, low_memory=False)

unii = pd.read_csv('unii_records.tsv', sep='\t', low_memory=False)
# add suffix onto column names
unii.columns = unii.columns.map(lambda x: str(x) + '_from_unii')
unii = unii.rename(columns={'UNII_from_unii': 'UNII'})

df = pd.merge(ginas, unii, on='UNII', how='left')
df.to_csv('fullSeedData-2016-06-16_UNII.csv')