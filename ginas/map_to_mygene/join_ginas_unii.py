#!/usr/bin/env python3

import pandas as pd
ginas = pd.read_csv('fullSeedData-2016-06-16.csv', index_col=0)
unii = pd.read_csv('unii_records.tsv', sep='\t')
df = pd.merge(ginas, unii, on='UNII', how='left')
df.to_csv('fullSeedData-2016-06-16_UNII.csv')