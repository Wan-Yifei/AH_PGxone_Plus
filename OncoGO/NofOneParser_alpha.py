#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 22:22:09 2018

@author: Dr. Pengfei.yu
@maintainer: Yifei Wan

Update:
# =============================================================================
# 07/26/2018    alpha version 0.0.1
# @Yifei.wan
# Summary
# Add new blocks into function xml2ActionNew() to extract 'prognosis & diagnosis 
# level', 'interaction' and corresponding PMIDs.
# =============================================================================
"""

import xml.etree.ElementTree as ET
import sys,pprint
import re
from ClinTrials.ClinTrialsUtil import *
from collections import OrderedDict


def extractPMID(text, PMIDs):
    '''
    Extract PMIDs from the paragraph text and replace the PMIDs with in-text reference

    :param text: paragraph text 
    :param PMIDs: previous list of PMIDs
    :returns: new_text: updated paragraph text; PMIDs: updated list of PMIDs after extract the PMID information from "text"

    :Example:

    >>> from NofOne.NofOneParser import *
    >>> PMIDs = ['12313450']
    >>> text = "Amplification of CCND1 has been described in multiple tumor types and has been reported to be correlated with overexpression of the Cyclin D1 protein, cell cycle progression, and cell proliferation (Quintayo et al., 2012; 22976805, Elsheikh et al., 2008; 17653856)"
    >>> new_text, PMIDs = extractPMID(text, PMIDs)
    >>> print PMIDs
    ['12313450','22976805','17653856']
    >>> print new_text
    "Amplification of CCND1 has been described in multiple tumor types and has been reported to be correlated with overexpression of the Cyclin D1 protein, cell cycle progression, and cell proliferation (Quintayo et al., 2012, Elsheikh et al., 2008)"

    '''
    pattern = r'\((.*?)\)'  # find all parenthesis
    for m in re.findall(pattern, text):
        PMIDs.extend(re.findall(r'\d{7,8}',m))
    big_regex = re.compile('|'.join(re.escape("; "+pmid) for pmid in PMIDs))
    new_text = big_regex.sub("", text)
    return new_text, PMIDs

def xml2Action(xml): 
    '''
    Extract actionable information from NofOne's output xml file.

    :param xml: xml output file from N-of-One   
    :returns: "total_info": all intepretation information for each actionable mutation; "Guideline": guideline information to be added to the first page; "PMIDs": list of PMID; "patient_condition": disease of patient in N-of-One's output

    :Example: 

    >>> import pprint
    >>> from NofOne.NofOneParser import *
    >>> total_info, Guideline, PMIDs, patient_information = xml2Action(xml)
    >>> pprint.pprint(total_info)
    >>> pprint.pprint(Guideline) 
    >>> print(PMIDs)
    >>> print(patient_information)
   
    '''
    tree = ET.ElementTree(file=xml)
    root = tree.getroot()

    ## use the new parwer if find element with new format specific names
    if root.find("detailed-biomarker-information")!=None:
        return xml2ActionNew(xml)

    PMIDs = []

    '''content for the first 3 tables, gene, therapyO, therapyS, therapyO, mutation, and pathway '''

    Mutation_total_info={}
    Guideline = {}
    patient_information = {}
    patient_information['disease'] = root.attrib['disease']
    patient_information['snomed_id'] = root.attrib['snomed-concept-id']

    for elem in tree.iter(tag='positive-result'):
        resultdict = {}
        if elem.attrib['variant-curated']=="No": continue  # remove the variants with no curation
        Mutation = elem.attrib['biomarker']+"-"+elem.attrib['result-value']
        if elem.attrib.has_key('therapies-approved-in-disease'):
            resultdict['therapyS'] = elem.attrib['therapies-approved-in-disease']
        else: resultdict['therapyS'] = None
        if elem.attrib.has_key('approved-in-other-diseases'):
            resultdict['therapyO'] = elem.attrib['approved-in-other-diseases']
        else: resultdict['therapyO'] = None
        if elem.attrib.has_key('therapies-associated-resistance'):
            resultdict['therapyR'] = elem.attrib['therapies-associated-resistance']
        else: resultdict['therapyR'] = None
        resultdict['pathway'] = elem.attrib['pathway']
        Mutation_total_info[Mutation]=resultdict

    ''' Guideline information '''
    for elem in tree.iter(tag="guideline"):
        Gene = elem.attrib['biomarkers']
        Guideline[Gene]=elem.find('content').text

    ''' content for the gene description and clinical trials '''

    for elem in tree.iter(tag='biomarker-content'):
        Gene = elem.attrib['marker']
        Alteration = elem.find('biomarker-summary/alterations/alteration').attrib['alteration-name']
        Mutation = Gene+"-"+Alteration
        if Mutation not in Mutation_total_info: continue  # remove the variants with no curation
        for ee in tree.iter(tag='glossary-item'):
            if Gene == ee.find('biomarker').text:
                Mutation_total_info[Mutation]['comment'] = ee.find('description').text
        Mutation_total_info[Mutation]['location'], PMIDs = extractPMID(elem.find('molecular-function/content').text, PMIDs)
        Mutation_total_info[Mutation]['prevalence'], PMIDs = extractPMID(elem.find('incidence/content').text, PMIDs)
        Mutation_total_info[Mutation]['effect'], PMIDs = extractPMID(elem.find('biomarker-summary/content').text, PMIDs)
        Mutation_total_info[Mutation]['role'], PMIDs = extractPMID(elem.find('role-in-disease/content').text, PMIDs)
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
    PMIDs = list(OrderedDict.fromkeys(PMIDs))
    return Mutation_total_info, Guideline, PMIDs, patient_information



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
    
def xml2ActionNew(xml): 
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
    tree = ET.ElementTree(file='/home/ywan/project/demo.xml')
    root = tree.getroot()            
    PMIDs = []
    Mutation_total_info={}
    Guideline = {}
    patient_information = {}
    interactions = {}
    
    '''# 1. content for the first 3 tables, gene, therapyO, therapyS, therapyO, mutation, and pathway '''
    # yifei: dict for prognostic and dignostic info    
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
    
    '''#2. yifei: Prognostic and dignostic level '''
    for elem in tree.iter(tag='positive-result'):
        if elem.attrib['variant-curated']=="No": 
            continue
        Mutation = elem.attrib['biomarker']+"-"+elem.attrib['result-value']
    
        Mutation_total_info[Mutation]['diagnostic-significance'] = elem.attrib['diagnostic-level-of-evidence']
        Mutation_total_info[Mutation]['prognostic-significance'] = elem.attrib['prognostic-level-of-evidence']    
    
    '''#3. Guideline information '''
    for elem in tree.iter(tag="guideline"):
        Biomarker = elem.find('biomarkers/biomarker')
        Mutation = Biomarker.attrib['marker']+"-"+Biomarker.attrib['alteration']
        Guideline[Mutation]=elem.find('content/item/text').text
        #break
            
    '''#4. yifei: Interaction '''
    
    ref_interaction = []
    for elem in tree.findall('interactions/interaction'):
        print(elem)
        interaction = [biomarker.attrib['marker'] + '-' + biomarker.attrib['alteration'] for biomarker in elem.findall('interaction-biomarkers/biomarker')]    
        Mutation_total_info[interaction[0]]['interaction'] = ' with '.join(interaction)
        Mutation_total_info[interaction[1]]['interaction'] = ' with '.join(interaction)
        ## yifei: extract PMIDs form summary
        interactions[' with '.join(interaction)], ref_interaction = extractPMID(elem.find('interaction-summary').text, PMIDs)
    
    # yifei: If mutation doesn't have interaction, value = Not found
    for mutation in Mutation_total_info.keys():
        try:
            #print(Mutation_total_info[mutation]['interaction'])
            Mutation_total_info[mutation]['interaction']
        except:
            Mutation_total_info[mutation]['interaction'] = 'Not found'
          
    # yifei: clean PMID or ref_interaction will be recorded twice    
    PMIDs = []    
        
    '''#5. content for the gene description and clinical trials '''
    ''' yifei: PMID of prognosis and dignosis would be updated inside blow loop '''
    
    for elem in tree.iter(tag='biomarker-content'):
        Gene = elem.attrib['marker']
        Alteration = elem.attrib['alteration-name']
        Mutation = Gene+"-"+Alteration
        if Mutation not in Mutation_total_info: continue  # remove the variants with no curation
        for ee in tree.iter(tag='glossary-item'):
            if Gene == ee.find('biomarker').text:
                Mutation_total_info[Mutation]['comment'] = ee.find('description').text
                
        # yifei: prognosis and dignosis
        Mutation_total_info[Mutation]['diagnosis'], PMIDs = parseSectionWithItems(elem.find('diagnostic-significance/variant'), PMIDs)
        Mutation_total_info[Mutation]['prognosis'], PMIDs = parseSectionWithItems(elem.find('prognostic-significance/variant'), PMIDs)
        # yifei: connect PMIDs with interactions
        PMIDs = PMIDs + ref_interaction
        # yifei: PMID for 'Gene info'
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
    PMIDs = list(OrderedDict.fromkeys(PMIDs))
    return Mutation_total_info, Guideline, PMIDs, patient_information, interactions



def Main():
    '''
    For testing purpose
    '''
    xml = sys.argv[1]
    total_info, Guideline, PMIDs, patient_information = xml2Action(xml)
    pprint.pprint(total_info)
    pprint.pprint(Guideline)
    pprint.pprint(patient_information)


if __name__=="__main__":
    Main()






