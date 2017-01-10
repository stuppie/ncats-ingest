#!/usr/bin/env bash

# download ginas gsrs data
# https://tripod.nih.gov/ginas/#/gsrs/release
# https://tripod.nih.gov/ginas/#/gsrs/data
# Download FDA data (2016-06-16)
wget https://tripod.nih.gov/ginas/gsrs/fullSeedData-2016-06-16.gsrs

# take only the third column
zcat fullSeedData-2016-06-16.gsrs | cut -f3- | gzip > fullSeedData-2016-06-16.json.gz

# make ID csv
./summarize_gsrs.py <(zcat fullSeedData-2016-06-16.json.gz) fullSeedData-2016-06-16.csv

# download UNII mapping file and extract mappings
wget https://fdasis.nlm.nih.gov/srs/download/srs/UNII_Data.zip
unzip -pc UNII_Data.zip "*Records*" > unii_records.tsv

# left join GINAS data and UNII data on the "UNII" field
./join_ginas_unii.py