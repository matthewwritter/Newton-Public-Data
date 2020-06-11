""" Author: Benyamin Meschede-Krasa 
script_description """
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

######################
######  PARAMS  ######
######################
FP_EER = os.path.join('data','eer16.csv')
FP_EER_CLEAN_CSV = os.path.join('data','eer16_clean.csv')
FP_EER_CLEAN_FEATHER = os.path.join('data','eer16_clean.feather')


#############################
######  PRECONDITIONS  ######
#############################
assert os.path.exists(FP_EER)

# preprocess to drop unecessary rows
eer  = pd.read_csv(FP_EER)
eer.rename(columns={'Unnamed: 11': 'extra'},inplace=True)

# drop NaN
eer = eer.dropna(thresh=3).reset_index(drop=True)
# drop duplicates
eer.drop_duplicates(keep=False,inplace=True,ignore_index=True)
# drop repeat of headers not picked up as duplicate
drop_idxs = np.argwhere(['Employee Name' in np.array(row) for idx,row in eer.iterrows()])[0]
eer.drop(drop_idxs,inplace=True)



# Fix issue of shifted columns (both overtime and extra have a shift)
# first for `overtime` column
## isolate shifted indices
mask = (eer.Overtime.isna())
eer_shift = eer[mask]

##fix shifted rows
cols = eer_shift.columns[:-1]
eer_shift.drop('Overtime',axis=1,inplace=True)
eer_shift.columns = cols
eer_shift['extra'] = np.nan

## replace shifted rows into og df
eer.loc[mask,:] = eer_shift

# now for `extra` column
## save non-shifted indices
mask = (eer.extra.isna())
eer_valid = eer[mask]

##fix shifted rows
cols = eer.columns[:-1]
eer.drop('Regular',axis=1,inplace=True)
eer.columns = cols

## restore valid rows
eer.loc[mask,:] = eer_valid

# make all pay columns numeric
eer.loc[:,'Other'] = eer.Other.str.replace(',','')
eer.loc[:,'Regular':] = eer.loc[:,'Regular':].astype(float)

# QC by checking totals
for idx, row in eer.iterrows():
    pay = row['Regular':'Other']
    pay_total = row['Total Pay']
    assert np.round(pay.sum(),2) == pay_total

# set data types
eer = eer.infer_objects().reset_index(drop=True)
eer.loc[:,:'Job Title'] = eer.loc[:,:'Job Title'].astype('category')

# save cleaned csv
eer.to_csv(FP_EER_CLEAN_CSV)
eer.to_feather(FP_EER_CLEAN_FEATHER)