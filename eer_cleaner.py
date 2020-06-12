""" Author: Benyamin Meschede-Krasa 
script_description """
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tabula

######################
######  PARAMS  ######
######################

COLUMNS = ['Department',
           'Employee Name',
           'Job Title',
           'Regular',
           'Overtime',
           'Detail',
           'Longevity',
           'Incentive',
           'Severance',
           'Other',
           'Total Pay']


def clean_pdf(fp_pdf):
    """pdf scraper for employee earnings reports from 
    Employee earnings reports for Newton, MA

    Parameters
    ----------
    fp_pdf : str
        filepath to a the publicly available pdf of the earnings reports

    Returns
    -------
    DataFrame
        earnings report for each employee as a dataframe
    """
    tables = tabula.read_pdf(fp_pdf,
                          pages="all",
                          multiple_tables=True)
                        #   pandas_options={'header':'infer'})
    tables_clean = []
    for table in tables:
        # drop NaN
        table = table.dropna(thresh=3).reset_index(drop=True)
        if table.isna().any().any():
            table.dropna(thresh=3,axis=1,inplace=True)
            table.columns = COLUMNS
        else:
            table.columns = COLUMNS
        
        tables_clean.append(table)
    
    # drop duplicates
    eer = pd.concat(tables_clean).drop_duplicates(keep=False,ignore_index=True)
    
    # clean commas for conversion to float
    for pay_type in COLUMNS[2:]:
        eer.loc[:,pay_type] = eer[pay_type].str.replace(',','')
    eer.loc[:,'Regular':] = eer.loc[:,'Regular':].astype(float)
    eer = eer.infer_objects().reset_index(drop=True)
    eer.loc[:,:'Job Title'] = eer.loc[:,:'Job Title'].astype('category')

    # Quality Control by checking totals are correct
    for _, row in eer.iterrows():
        pay = row['Regular':'Other']
        pay_total = row['Total Pay']
        assert np.round(pay.sum(),2) == pay_total, f"Totals dont add up for {row}"
    
    return eer

if __name__ == "__main__":
    ## Params
    FP_EER19_PDF = os.path.join('data','eer19.pdf')
    FP_EER_CSV = os.path.join('data','eer19.csv')
    FP_EER_FEATHER = os.path.join('data','eer19.feather')
    
    ## Preconditions
    assert os.path.exists(FP_EER19_PDF)
    
    eer = clean_pdf(FP_EER19_PDF)
    eer.to_csv(FP_EER_CSV)
    eer.to_feather(FP_EER_FEATHER)