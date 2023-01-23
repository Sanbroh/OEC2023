#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 19:22:12 2023

@author: thomastesselaar
"""


import pandas as pd
hosp_data = pd.read_csv("hospital_data.csv", index_col='seq')

# {0:CAD, 1:Arthritis, 2:Weakened Immune System, 3:Leukemia, 4:Asthma, 
# 5:Light Allergies, 6:Severe Allergies}
uses_ccu = [0]
uses_vc = [4]
uses_tc = []


# {0:Mild pain, 1:Severe pain, 2:Diarrhea, 3:Vomiting, 4:Open bleeding, 5:Cramping
# 6:Mild fever, 7:High fever, 8:Fatigue, 9:Nose Bleeds, 10:Weight loss, 11:Short of breath
# 12:Unconscious, 13:Cough, 14:Chest Pain, 15:Lack of Taste, 16:Confusion, 
# 17:Loss of Appetite, 18:AB pain, 19:Nausea}
needs_icu = [1, 4, 7, 12, 14]
needs_ccu = [14]
needs_vc = [11, 13]
needs_tc = [12, 16]

def get_best_hospitals(city:str, age:int, sex:str, underlying, 
                       symptoms, urgency:int, time:str = "12:00", print_results = True):
    """
    

    Parameters
    ----------
    city : str
        The name of the city.
    age : int
        Age of patient.
    sex : str
        Sex of patient.
    underlying : iterable (set or list)
        The underlying conditions of the patient.
    symptoms : iterable (set or list)
        The symptoms of the patient.
    urgency : int
        0 for not urgent, i.e can go later, 1 for should go now but not at 
        immediate risk of death or permanent injury, 2 for very urgent, needs 
        ER or maybe ICU.
    time : str
        The time of day, used to check if hospitals are open.
    print_results : bool
        If True, prints the hospitals to the terminaldd

    Returns
    -------
    A list of the ID's of the recommended hospitals, in order.

    """
    
    city = city.lower()
    city_coords = {"bowmanville":[43.913043, -78.689617], "brampton":[43.685271, -79.759924],
                   "burlington":[43.3487, -79.7903], "cambridge":[43.3616211, -80.3144276],
                   "cobourg":[43.9593373, -78.1677363], "collingwood":[44.5007687, -80.2169047],
                   "cornwall":[45.0212762, -74.730345], "etobicoke":[43.6204946, -79.5131983],
                   "gatineau":[45.4765, -75.7013], "guelph":[43.539102, -80.247622], 
                   "hamiltion":[43.243603, -79.889075], "kingston":[44.263565, -76.50336],
                   "kitchener":[43.434311, -80.477747], "london":[42.979398, -81.246138],
                   "markham":[43.8833333, -79.25], "mississauga":[43.548599, -79.626427],
                   "niagara falls":[43.1064104, -79.0674185], "ottawa":[45.411572, -75.698194],
                   "puslinch":[43.4329, -80.0973], "thunder bay":[48.415802, -89.2673],
                   "timmins":[48.4758208, -81.3304953], "toronto":[43.6525, -79.3816667],
                   "waterloo":[43.4643, -80.5204], "windsor":[42.3149, -83.0364],
                   "woodstock":[43.1315, 80.7472],
                   }
    if(not city_coords[city]):
        print("We have not yet added support for this city :(")
        return -1
    lat = city_coords[city][0]
    long = city_coords[city][1]
    
    
    scores = [0 for i in range(40)]
    
    for i in range(40):
        
        
        hosp_distance = ((hosp_data.loc[(i+1), "latitude"]-lat)**2 + (hosp_data.loc[(i+1), "longitude"]-long)**2)**(1/2)
        scores[i] += 30 - (urgency + 3)*6*hosp_distance
        
        
        # Don't recommend childrens hospital to adults
        childrens_hospitals = [10, 23, 32]
        if (i in childrens_hospitals):
            if (age > 18):
                scores[i] -= 18
                continue
            else:
                scores[i] += 8
        
        # Need an open hospital if urgent
        if (urgency >= 1):
            opening_time = hosp_data.loc[(i+1), "opening"]
            closing_time = hosp_data.loc[(i+1), "closing"]
            if (time >= closing_time or time <= opening_time):
                scores[i] -= 18
                continue
            
        # If they need icu
        if hosp_data.loc[i+1, "icu"] == 'yes':
            for s in symptoms:
                if s in needs_icu:
                    scores[i] += 1
            
        else:
            if (urgency == 2):
                scores -= 1
                    
        # If they need ccu
        if hosp_data.loc[i+1, "ccu"] == 'yes':
            for s in symptoms:
                if s in needs_ccu:
                    scores[i] += 1
            for u in underlying:
                if u in uses_ccu:
                    scores[i] += 1
                    
        # If they need vc
        if hosp_data.loc[i+1, "vc"] == 'yes':
            for s in symptoms:
                if s in needs_vc:
                    scores[i] += 1
            for u in underlying:
                if u in uses_vc:
                    scores[i] += 1
        
        # If they need tc
        if hosp_data.loc[i+1, "tc"] == 'yes':
            for s in symptoms:
                if s in needs_tc:
                    scores[i] += 1
            for u in underlying:
                if u in uses_tc:
                    scores[i] += 1
        
        
        # Consider hospital size
        if (urgency == 2 and hosp_data.loc[(i+1), "capacity"] in ['a', 'b']):
            scores[i] += 2
                
        if (urgency == 1 and hosp_data.loc[(i+1), "capacity"] in ['a', 'b', 'c']):
            scores[i] += 1
            
        if (urgency == 0 and hosp_data.loc[(i+1), "capacity"] in ['n']):
            scores[i] += 1
        
        # lt = hosp_data.loc[(i+1), "latitude"]
        # ln = hosp_data.loc[(i+1), "longitude"]
        
        # print("{")
        # print(f"    \'lat\': {lt},")
        # print(f"    \'lng\': {ln},")
        # print("},")
        
        # print(hosp_distance)
    
    scores = [(i+1, scores[i]) for i in range(40)]
    scores = sorted(scores, key=lambda x: x[1], reverse = True)
    
    # The number of hospitals to show
    n = 5
    bed_capacity = {'a':"Large hospital; 100+ beds", 'b':"Medium sized hospital; 100+ beds", 
                    'c':"Small hospital; <100 beds", 'n':"Clinic or pharmacy"}
    
    # Prints out the recommended hospital with relevant information
    for i in range(12):
        no = scores[i][0]
        if(print_results):
            print(str(i+1) + ". -------------------------------")
            print('Name: ' + str(hosp_data.loc[no, "facilityname"]))
            print('Hours: ' + hosp_data.loc[no, "opening"] + "-" + hosp_data.loc[no, "closing"])
            print('Contact number: ' + str(hosp_data.loc[no, "contact"]))
            print('Hospital Size: ' + bed_capacity[hosp_data.loc[no, "capacity"]] + '\n')
        
        if i >= 5:
            n = i+1
            if scores[i][1] < 18:
                break
            
    # Gets a list of the hospital IDs
    hospitals = [scores[h][0] for h in range(n)]
    # print(hospitals)
    
    # returns list of hospital IDs
    return hospitals


def print_test_results_to_csv():
    test_cases = [["Collingwood", 24, "F", {}, {1, 5}, 1, "12:00"],
                  ["Puslinch", 64, "M", {0, 1, 2}, {2, 3, 5, 6}, 1, "12:00"],
                  ["Timmins", 33, "M", {3}, {7, 8, 9, 10, 11}, 2, "12:00"],
                  ["Gatineau", 15, "M", {}, {12}, 2, "12:00"],
                  ["Kingston", 20, "F", {4}, {6, 11, 12, 13, 14, 15, 16}, 2, "12:00"],
                  ["Woodstock", 3, "M", {5}, {2, 3, 17, 18}, 1, "12:00"]]
    
    results = []
    
    for i, case in enumerate(test_cases):
        results.append([i+1, get_best_hospitals(case[0], case[1], case[2], case[3], case[4], case[5], case[6], print_results=False)])
    
    df = pd.DataFrame(results, columns=['Test Case', 'Hospitals']) 
    
    df.to_csv("CareFull_-_OEC_2023_Programming_Submission_Output.csv")
    
    print(df)
    


get_best_hospitals("Collingwood", 24, "F", {}, {1, 5}, 1, "12:00")

# print_test_results_to_csv()







