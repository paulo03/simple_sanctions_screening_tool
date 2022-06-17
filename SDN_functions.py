import pandas as pd
import requests
import json
from datetime import datetime
from fuzzywuzzy import fuzz, process

def name_match(name, sdn_name, match_type):
    '''function takes 3 args, 2 different names and a match type,
       and will return a bool based on match criteria'''
    types = ['EXACT', 'STRONG', 'MEDIUM', 'LIGHT']
    if match_type not in types:
        print('ERROR: match_type does not exist - Only "EXACT",' + \
              '"STRONG", "MEDIUM", "LIGHT"')
        return []
    else:
        exact_match = fuzz.ratio(name, sdn_name)
        partial_match = fuzz.partial_ratio(name, sdn_name)
        # EXACT MATCH
        if match_type == types[0]:
            if exact_match == 100:
                return True
            else:
                return False
        
        # STRONG MATCH
        elif match_type == types[1]:
            if partial_match >= 85:
                return True
            else:
                return False
        
        # MEDIUM MATCH
        elif match_type == types[2]:
            if partial_match >= 70:
                return True
            else:
                return False
        
        # LIGHT MATCH
        else:
            if partial_match >= 55:
                return True
            else:
                return False

def indiv_name_match(last_name, first_name, dataframe, match_type):
    # Check Last Name matches
    last_name_matches = []
    count = 0
    while count < len(dataframe):
        is_match = name_match(last_name,
                              dataframe['Last Name'][count],
                              match_type)
        if is_match == True:
            last_name_matches.append(dataframe['#'][count])
        count += 1
    # Check First Name matches on Filtered DataFrame
    # (with only Last Name matches in it)
    first_name_matches = []
    last_name_match_df = dataframe[dataframe['#'].isin(last_name_matches)]
    last_name_match_df.reset_index(inplace=True)
    count = 0
    while count < len(last_name_match_df):
        is_match = name_match(first_name,
                              last_name_match_df['First Name'][count],
                              match_type)
        if is_match == True:
            first_name_matches.append(last_name_match_df['#'][count])
        count += 1
    # Check if there are any name matches, if there are, then check
    # whether the DOB matches
    both_name_match_df = last_name_match_df[last_name_match_df['#'].isin(
        first_name_matches)]
    return both_name_match_df

def DOB_match(indiv_dob, sdn_dob):
    '''function takes 2 args, 2 different DOBs with possibly different
       formats and returns bool based on match'''
    # convert individual's DOB into datetime format
    indiv_dob = datetime.strptime(indiv_dob, "%d %b %Y")
    # Length of SDN DOB, will help us understand how to convert to datetime
    sdn_dob_len = len(sdn_dob) 
    months = {'JAN': [1, 31], 'FEB': [2, 29], 'MAR': [3, 31], 'APR': [4, 30],
              'MAY': [5, 31], 'JUN': [6, 30], 'JUL': [7, 31], 'AUG': [8, 31],
              'SEP': [9, 30], 'OCT': [10, 31], 'NOV': [11, 30], 'DEC': [12, 31]
              }
    months_num = {'1': 31, '2': 28, '3': 31, '4': 30, '5': 31, '6': 30, 
                  '7': 31, '8': 31, '9': 30, '10': 31, '11': 30, '12': 31}
    
    if sdn_dob == '-0-':
        # Return "MATCH" or True, because the SDN List individual does not
        # have DOB accessible
        print('NOTE: No DOB on SDN List for this Individual')
        return True
    else:
        # SDN List DOB is not -0-/blank and we must check for all the
        # variations of DOBs listed
        if 'circa' not in sdn_dob: # Exact DOB (not a range)
            if sdn_dob_len == 4:
                # sdn_dob Format is '1999'
                if indiv_dob >= datetime(int(sdn_dob), 1, 1) \
                   and indiv_dob <= datetime(int(sdn_dob), 12, 31):
                    return True
                else:
                    return False
            elif sdn_dob_len == 8:
                # sdn_dob Format is 'Jan 1999'
                # Start of month
                start = datetime(int(sdn_dob.split()[1]),
                                 months[sdn_dob.split()[1]][0], 1)
                # End of month
                end = datetime(int(sdn_dob.split()[1]), 
                               months[sdn_dob.split()[1]][0], 
                               months[sdn_dob.split()[1]][1],)
                if indiv_dob >= start and indiv_dob <= end:
                    return True
                else:
                    return False
            elif sdn_dob_len == 11:
                # sdn_dob Format is '01 Jan 1999'
                if indiv_dob == datetime.strptime(sdn_dob, "%d %b %Y"):
                    return True
                else:
                    return False
            elif sdn_dob_len == 12:
                # sdn_dob Format is '1998 to 1999'
                if indiv_dob >= datetime(int(sdn_dob.split()[0]), 1, 1) \
                   and indiv_dob <= datetime(int(sdn_dob.split()[2]), 12, 31):
                    return True
                else:
                    return False
            elif sdn_dob_len == 26:
                # sdn_dob Format is '01 Jan 1999 to 31 Dec 1999'
                start = datetime.strptime(sdn_dob.split(' to ')[0], "%d %b %Y")
                end = datetime.strptime(sdn_dob.split(' to ')[1], "%d %b %Y")
                if indiv_dob >= start and indiv_dob <= end:
                    return True
                else:
                    return False
            else:
                print('WARNING: Not an expected DOB Format from SDN List ' \
                      + '--> {}'.format(sdn_dob))
                # For now, if there are any other DOB formats,
                # just return True instead of False
                return True
        else:
            # 'circa' is in SDN DOB and now we have to check against wider
            # range for DOB
            if sdn_dob_len == 10:
                # sdn_dob Format is 'circa 1999'
                # check if Individual DOB is within sdn_dob +/- 3 years
                start = datetime(int(int(sdn_dob.split()[1])-3), 1, 1)
                end = datetime(int(int(sdn_dob.split()[1])+3), 12, 31)
                if indiv_dob >= start and indiv_dob <= end:
                    return True
                else:
                    return False
            elif sdn_dob_len == 17:
                # sdn_dob Format is 'circa 01 Jan 1999'
                # check if Individual DOB is within sdn_dob +/- 3 months
                sdn_dob = sdn_dob.split('circa ')[1]
                month = sdn_dob.split()[1].upper()
                if month in ['JAN', 'FEB', 'MAR']:
                    # Minus 3 months puts into last year
                    start = datetime((int(sdn_dob.split()[2]) - 1),
                                     (months[month][0] + 9), 1)
                else:
                    start = datetime(int(sdn_dob.split()[2]),
                                     (months[month][0] - 3), 1)
                if month in ['OCT', 'NOV', 'DEC']:
                    # Add 3 months puts it into next year
                    end = datetime((int(sdn_dob.split()[2]) + 1), 
                                   (months[month][0] - 9), 
                                   months_num[str(int((months[month][0] - 9)))]
                                   )
                else:
                    end = datetime(int(sdn_dob.split()[2]), 
                                   (months[month][0] + 3), 
                                   months_num[str(int((months[month][0] + 3)))]
                                   )
                if indiv_dob >= start and indiv_dob <= end:
                    return True
                else:
                    return False
            elif sdn_dob_len == 15:
                # sdn_dob Format is 'circa 1979-1982'
                # check if Individual DOB is within sdn_dob +/- 3 years
                # of circa range
                start, end = sdn_dob.split()[1].split('-')
                # split 'circa 1979-1982'
                start = datetime((int(start) - 3), 1, 1)
                end = datetime((int(end) + 3), 12, 31)
                if indiv_dob >= start and indiv_dob <= end:
                    return True
                else:
                    return False
            else:
                print('WARNING: Not an expected DOB Format from SDN List ' \
                      + '--> {}'.format(sdn_dob))
                # For now, if there are any other DOB formats, just
                # return True instead of False
                return True

def get_individual_SDN():
        
        # Use Requests library to scrape web-hosted SDN List, store in
        # string var
        r = requests.get('https://www.treasury.gov/ofac/downloads/sdn.pip')
        lines = str(r.text).split("\r\n")
        
        # Take string variable and split it into list, based on pip formatting
        matrix = []
        for line in lines:
            entry = line.split("|")
            matrix.append(entry)
            
        # Create initial Individual Lists
        individual = []
        count = 0
        while count < len(matrix):
            if len(matrix[count]) > 1:
                if matrix[count][2] == '"individual"':
                    individual.append(matrix[count])
            count += 1
            
        # Create List and then DataFrame for Individuals on SDN List

        # Create List
        f_ind = []
        for entry in individual:
            try:
                last_name = entry[1].split(',')[0].strip('"')
                first_name = entry[1].split(',')[1].strip('"')
            except IndexError as e:
                last_name = entry[1].split(',')[0].strip('"')
                first_name = ""
            f_ind.append([
                int(entry[0]), 
                last_name,
                first_name[1:],
                entry[2].strip('"'),
                entry[3].strip('"'),
                entry[4].strip('"'),
                entry[11].strip('"')
            ])
            
        # Create DataFrame and add column which includes isolated DOB
        # where possible
        df_ind = pd.DataFrame(f_ind,
                      columns=["#", "Last Name", "First Name", 
                               "Ind/Entity", "Global Tag", "Note", "Extra"])
        # Initialize new column for DOB
        df_ind['DOB'] = '-0-'
        
        # Loop thru Extra column & split string based on DOB, assign DOB
        # to DOB column
        count = 0
        while count < len(df_ind):
            if 'DOB' in df_ind['Extra'][count]:
                dob = df_ind['Extra'][count][df_ind['Extra'][count].find(
                    'DOB')+4:]
                dob = dob[:dob.find(';')]
                df_ind.loc[count, 'DOB'] = dob
            count += 1
            
        return df_ind

def get_entity_SDN():
        
        # Use Requests library to scrape web-hosted SDN List,
        # store in string var
        r = requests.get('https://www.treasury.gov/ofac/downloads/sdn.pip')
        lines = str(r.text).split("\r\n")
        
        # Take string variable and split it into list, based on pip formatting
        matrix = []
        for line in lines:
            entry = line.split("|")
            matrix.append(entry)
            
        # Create initial Entity Lists
        entity = []
        count = 0
        while count < len(matrix):
            if len(matrix[count]) > 1:
                if matrix[count][2] != '"individual"':
                    entity.append(matrix[count])
            count += 1
        
        # Create List and then DataFrame for Entities on SDN List
        f_entity = [] # f for final list for corp
        for entry in entity:
            f_entity.append([
                int(entry[0]), 
                entry[1].strip('"'),
                entry[2].strip('"'),
                entry[3].strip('"'),
                entry[11].strip('"')
            ])
        df_entity = pd.DataFrame(f_entity, columns=["#", "Name", "Type",
                                                    "Country", "Extra"])
        
        return df_entity
