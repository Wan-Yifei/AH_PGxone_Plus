# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 17:51:50 2018

@author: pengfei.yu
@editor: yifei.wan
"""

import xml.etree.ElementTree as ET
#import sys,pprint
#import re

#tree = ET.parse('C:/Users/yifei.wan/Desktop/OncoGxOne/New_version/AMP demo-AML_COMPLETE.xml')
#root = tree.getroot()
#PMIDs = []

def parseItem(item):
    references = item.findall("references/reference")
    ref_short = ", ".join([x.find('authors').text.split(" ")[0]+" et al., "+x.find('year').text for x in references])
    if ref_short=="":
        text = item.find("text").text
    else:
        text = item.find("text").text.rstrip(".") + " (%s)."%(ref_short)
    return text

def parseSectionWithItems(Section, PMIDs):
    try:
        Texts = [parseItem(item) for item in Section.findall("content/item")]
        PMIDs.extend([ref.find("reference-id").text for ref in Section.findall("references/reference")])
        return " ".join(Texts), PMIDs
    except:
        return "", PMIDs
    
#def xml2ActionNew(xml): 
    '''
    Extract actionable information from NofOne's output xml file. This is a new parser for N-of-One's AMP based interpretation service
    :param xml: xml output file from N-of-One   
    :returns: "total_info": all intepretation information for each actionable mutation; "Guideline": guideline information to be added to the first page; "PMIDs": list of PMID; "patient_condition": disease of patient in N-of-One's output
    :Example: 
    >>> import pprint
    >>> from NofOne.NofOneParser import *
    >>> total_info, Guideline, PMIDs, patient_information = xml2ActionNew(xml)
    >>> pprint.pprint(total_info)
    >>> pprint.pprint(Guideline) 
    >>> print(PMIDs)
    >>> print(patient_information)
   
    '''
tree = ET.ElementTree(file=xml)
root = tree.getroot()            
PMIDs = []

'''# 1. content for the first 3 tables, gene, therapyO, therapyS, therapyO, mutation, and pathway '''

Mutation_total_info={}
Guideline = {}
patient_information = {}
# yifei: dict for prognostic and dignostic info
pro_dig_level = {}
patient_information['disease'] = root.attrib['disease']
patient_information['snomed_id'] = root.attrib['snomed-disease-concept-id']

for elem in tree.iter(tag='positive-result'):
    resultdict = {}
    if elem.attrib['variant-curated']=="No": continue  # remove the variants with no curation
    Mutation = elem.attrib['biomarker']+"-"+elem.attrib['result-value']

    resultdict['therapyS'] = ", ".join([x.attrib['drug-name'] for x in elem.findall('.//summary-therapy[@approval="This indication approved"][@effect="Sensitive"]')])
    if resultdict['therapyS']=="":
        resultdict['therapyS'] = None
    resultdict['therapyO'] = ", ".join([x.attrib['drug-name'] 
                              for x in elem.findall('.//summary-therapy[@approval="Other indication approved"][@effect="Sensitive"]') if x.attrib['therapeutic-level-of-evidence'] not in ['Not determined','D','E']])
    if resultdict['therapyO']=="":
        resultdict['therapyO'] = None
    resultdict['therapyR'] = ", ".join([x.attrib['drug-name'] 
                              for x in elem.findall('.//summary-therapy[@approval="This indication approved"][@effect="Resistant"]') if x.attrib['therapeutic-level-of-evidence'] in ['A', 'B']])
    if resultdict['therapyR']=="":
        resultdict['therapyR'] = None
    resultdict['pathway'] = elem.attrib['pathway']
    Mutation_total_info[Mutation]=resultdict
    

'''#2. Guideline information '''
for elem in tree.iter(tag="guideline"):
    Biomarker = elem.find('biomarkers/biomarker')
    Mutation = Biomarker.attrib['marker']+"-"+Biomarker.attrib['alteration']
    Guideline[Mutation]=elem.find('content/item/text').text

'''#3. yifei: Prognostic and dignostic level '''
for elem in tree.iter(tag='detailed-biomarker-information'):
    Biomark = elem.find('biomark-content')
    Gene = Biomark.attrib('marker')
    Alteration = Biomark.attrib('alteration-name')
    pro_dig_level['{}\t{}'.format(Gene, Alteration)] = Biomark.find('diagnostic-significance/variant').attrib['diagnostic-level-of-evidence'] \
    + '\t' + Biomark.find('prognostic-significance/variant').attrib['prognostic-level-of-evidence']
    

'''#4. content for the gene description and clinical trials '''

for elem in tree.iter(tag='biomarker-content'):
    Gene = elem.attrib['marker']
    Alteration = elem.attrib['alteration-name']
    Mutation = Gene+"-"+Alteration
    if Mutation not in Mutation_total_info: continue  # remove the variants with no curation
    for ee in tree.iter(tag='glossary-item'):
        if Gene == ee.find('biomarker').text:
            Mutation_total_info[Mutation]['comment'] = ee.find('description').text
    Mutation_total_info[Mutation]['location'], PMIDs = parseSectionWithItems(elem.find('molecular-function'), PMIDs)
    Mutation_total_info[Mutation]['prevalence'], PMIDs = parseSectionWithItems(elem.find('incidence'), PMIDs)
    Mutation_total_info[Mutation]['effect'], PMIDs = parseSectionWithItems(elem.find('./biomarker-summary[@content-type="clinical-relevance"]'), PMIDs)
    Mutation_total_info[Mutation]['role'], PMIDs = parseSectionWithItems(elem.find('role-in-disease'), PMIDs)
    Mutation_total_info[Mutation]['ClinicalTrials'] = []
    for CT in elem.findall('clinical-trials'):
        ClinType = CT.attrib['prioritized-by']
        for trial in CT.findall('clinical-trial'):
            markerdict = {}
            markerdict['Type'] = ClinType
            markerdict['Target'] = ", ".join([x.text for x in trial.findall('targets/target')])
            markerdict['id'] = trial.find('trial-id').text
            markerdict['title'] = trial.find('title').text
            markerdict['phase'] = trial.find('phase').text
            sets = []
            sites = trial.findall('trial-sites/trial-site')
            for site in sites: 
                if site.find('country').text == "United States":
                    loca = site.find('state').text
                else: loca = site.find('country').text
                sets.append(loca)
            unique_set = set(sets)
            markerdict['state'] = unique_set
            Mutation_total_info[Mutation]['ClinicalTrials'].append(markerdict)
    Mutation_total_info[Mutation]['therapies']={}
    for therapy in elem.findall('therapies/therapy'):
        if therapy.find("trade-name")==None: continue
        drug = therapy.find('drug-name').text
        Mutation_total_info[Mutation]['therapies'][drug]={}
        Mutation_total_info[Mutation]['therapies'][drug]['targets']=", ".join([x.text for x in therapy.findall('targets/target')])
        Mutation_total_info[Mutation]['therapies'][drug]['trade-name']=therapy.find("trade-name").text
        try:
            if therapy.find('status-in-other-indications/status').text=="FDA Approved":
                Mutation_total_info[Mutation]['therapies'][drug]['disease']=", ".join([x.text for x in therapy.findall('status-in-other-indications/disease-list/disease')])
        except:
            pass
        try:
            if therapy.find('status-in-this-indication/status').text=="FDA Approved":
                Mutation_total_info[Mutation]['therapies'][drug]['disease']=", ".join([x.text for x in therapy.findall('status-in-this-indication/disease-list/disease')])
        except:
            pass