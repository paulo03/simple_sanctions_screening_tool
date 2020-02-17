import pandas as pd
import requests
import json
from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from SDN_functions import *

class Individual:
    
    def __init__(self, last_name, first_name, dob):
        '''initialize object for individual, including their name and date
           of birth'''
        # Checking format of DOB before initializing variables for object
        # df of individuals on SDN List
        self.individual_list = get_individual_SDN()
        if len(dob) == 11:
            self.last_name = last_name
            self.first_name = first_name
            self.dob = dob
        else:
            print('FormatError: dob argument was not formatted correctly ' \
                  + '(Correct Format: "DD MM YYYY")')
            
    def get_self(self):
        '''return tuple of individual information, including name and date
           of birth'''
        try:  
            return (self.last_name, self.first_name, self.dob)
        except AttributeError as e:
            'function not initialized'
    
    def update_first_name(self, first_name):
        'update first name for individual'
        self.first_name = first_name
        
    def update_last_name(self, last_name):
        'update last name for individual'
        self.last_name = last_name
        
    def update_dob(self, dob):
        'update date of birth for individual'
        self.dob = dob
    
    def check_SDN(self, match_type):
        '''return DataFrame including individuals on the SDN List that match
           based on selected match type'''
        types = ['EXACT', 'STRONG', 'MEDIUM', 'LIGHT']
        return_list = []
        if match_type.upper() not in types:
            print('ERROR: string used for match_type does not exist')
            print('Only 4 strings accepted: "{}", "{}", "{}", and "{}"'
                  .format(types[0], types[1], types[2], types[3]))
            return True # Return True (different response than anything normal)
        
        # EXACT MATCH == DOB match needed, Name match exact
        if match_type.upper() == types[0]:
            both_name_match_df = indiv_name_match(self.last_name,
                                                  self.first_name, 
                                                  self.individual_list,
                                                  match_type.upper())
            if len(both_name_match_df) != 0:
                both_name_match_df.reset_index(inplace=True)
                count = 0
                while count < len(both_name_match_df):
                    dob_match = DOB_match(self.dob,
                                          both_name_match_df['DOB'][count])
                    if dob_match == True:
                        return_list.append(both_name_match_df['#'][count])
                    count += 1
        
        # STRONG MATCH == DOB match needed, Name match fuzzy logic
        elif match_type.upper() == types[1]:
            both_name_match_df = indiv_name_match(self.last_name,
                                                 self.first_name, 
                                                 self.individual_list,
                                                 match_type.upper())
            if len(both_name_match_df) != 0:
                both_name_match_df.reset_index(inplace=True)
                count = 0
                while count < len(both_name_match_df):
                    dob_match = DOB_match(self.dob,
                                          both_name_match_df['DOB'][count])
                    if dob_match == True:
                        return_list.append(both_name_match_df['#'][count])
                    count += 1
            
        # MEDIUM MATCH == DOB match needed, Name match fuzzy logic less strong
        elif match_type.upper() == types[2]:
            both_name_match_df = indiv_name_match(self.last_name,
                                                 self.first_name, 
                                                 self.individual_list,
                                                 match_type.upper())
            if len(both_name_match_df) != 0:
                both_name_match_df.reset_index(inplace=True)
                count = 0
                while count < len(both_name_match_df):
                    dob_match = DOB_match(self.dob,
                                          both_name_match_df['DOB'][count])
                    if dob_match == True:
                        return_list.append(both_name_match_df['#'][count])
                    count += 1
            
        # LIGHT MATCH == DOB match not needed, Name match fuzzy logic
        # least strong
        elif match_type.upper() == types[3]:
            both_name_match_df = indiv_name_match(self.last_name,
                                                 self.first_name, 
                                                 self.individual_list,
                                                 match_type.upper())
            if len(both_name_match_df) != 0:
                both_name_match_df.reset_index(inplace=True)
                count = 0
                while count < len(both_name_match_df):
                    return_list.append(both_name_match_df['#'][count])
                    count += 1
            
        if len(return_list) != 0:
            return_df = both_name_match_df[both_name_match_df['#'].isin(
                return_list)]
            final_return_df = return_df.drop(columns=['level_0', 'index'])
            return final_return_df
        else:
            return False

class Entity:
    
    def __init__(self, entity_name):
        'initialize object for entity, including their name'
        self.entity_list = get_entity_SDN() # df of entities on SDN List
        self.name = entity_name
    
    def get_self(self):
        'return entity_name'
        return self.name
    
    def update_name(self, new_entity_name):
        'update name for entity'
        self.name = new_entity_name
        
    def check_SDN(self, match_type):
        '''return DataFrame including entities on the SDN List that match
           based on selected match type'''
        types = ['EXACT', 'STRONG', 'MEDIUM', 'LIGHT']
        return_list = []
        if match_type.upper() not in types:
            print('ERROR: string used for match_type does not exist')
            print('Only 4 strings accepted: "{}", "{}", "{}", and "{}"'
                  .format(types[0], types[1], types[2], types[3]))
            return True # Return True (different response than anything normal)
        
        name_matches = []
        count = 0
        while count < len(self.entity_list):
            is_match = name_match(self.name,
                                  self.entity_list['Name'][count],
                                  match_type.upper())
            if is_match == True:
                name_matches.append(self.entity_list['#'][count])
            count += 1
        if len(name_matches) == 0:
            return False
        else:
            return_df = self.entity_list[self.entity_list['#'].isin(
                name_matches)]
            return_df.reset_index(inplace=True)
            final_return_df = return_df.drop(columns=['index'])
            return final_return_df        
