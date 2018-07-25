import sys, codecs, subprocess, argparse, os, re
scriptFolder = os.path.dirname(os.path.abspath(sys.argv[0]))+"/"
sys.path.append(scriptFolder)
sys.path.append("/home/pengfei.yu/Softwares")
from VCFmodules.VCFutility import *
from ClinAccToMutationName import *
from ClinTrials.ClinTrialsUtil import *
from NofOne.NofOneParser import *
from pymedtermino.snomedct import *
from ClinTrials.state_graph import *
from VCFmodules.SnpEff import *
from VCFmodules.GeneInfo import *
GI = GeneInfo(local_file=scriptFolder+"/GeneInfo.txt")
PM = PubMed(local_file=scriptFolder+"/PubMed_info.txt")

sys.stdout = codecs.getwriter('utf8')(sys.stdout)


def ParseArg():
    p = argparse.ArgumentParser(description="generate OncoGxOne interpretation file with clinvar annotated VCF file, coverage file, fusionmap output and mutation/drug information", epilog="Need: VCFutility")
    p.add_argument("VCFfile",type=str, help="clinvar annotated VCF file")
    p.add_argument("fusionOutput",type=str, help="fusionmap or factera output")
    p.add_argument("CNV",type=str, help="CNV output file")
    p.add_argument("XML",type=str, help="NofOne's output XML file (complete)")
    #p.add_argument('-c',"--condition",type=str)
    #p.add_argument('-t','--therapy',type=str,default="/home/pengfei.yu/OncoGxOne/pipeline/OncoGxOne_knowledgebase_main_20151218.txt",help="mutation to therapy database file, default: OncoGxOne_knowledgebase_main_20151218.txt")
    p.add_argument('-s','--state',type=str,default='NJ', help="patient's state, two-letter abbreviation")
    p.add_argument("-d","--depth",type=int,default=50, help="minimum depth requirement, default: 50")
    p.add_argument("-q","--qual",type=float, default=30.0, help="minmum quality requirement, default: 30.0")
    p.add_argument("-f","--freq",type=float,default=0.02, help="minimum frequency requirement, default: 0.02")
    p.add_argument("-o","--output",type=str,help="output file name")
    if len(sys.argv)==1:
        print >>sys.stderr,p.print_help()
        sys.exit(0)
    return p.parse_args()

args = ParseArg()
min_depth = args.depth
min_qual = args.qual
min_freq = args.freq
state = args.state
output = codecs.open(args.output,'w',encoding='utf-8')
total_info, Guideline, PMIDs, patient_information = xml2Action(args.XML)
#output = sys.stdout
Sample_name = args.CNV.split("_CNV")[0]

transcript_file = open(scriptFolder+"Admera_preferred_transcript_07DEC2015.txt",'r')
preferred_transcript={}
for l in transcript_file.read().split("\n"):
    if l.strip()=="" or l.startswith("Gene"): continue
    lsep = l.strip().split("\t")
    if lsep[0] not in preferred_transcript:
        if len(lsep)>2:
            preferred_transcript[lsep[0]]=lsep[1].strip().split(" or ")+lsep[2].strip().split(" or ")
        else:
            preferred_transcript[lsep[0]]=lsep[1].strip().split(" or ")
transcript_file.close()



def searchSnomedID(description):
    for i in SNOMEDCT.search(description):
        if i.term.endswith("(disorder)"):
            return i

state_to_code = {"VERMONT": "VT", "GEORGIA": "GA", "IOWA": "IA", "Armed Forces Pacific": "AP", "GUAM": "GU", "KANSAS": "KS", "FLORIDA": "FL", "AMERICAN SAMOA": "AS", "NORTH CAROLINA": "NC", "HAWAII": "HI", "NEW YORK": "NY", "CALIFORNIA": "CA", "ALABAMA": "AL", "IDAHO": "ID", "FEDERATED STATES OF MICRONESIA": "FM", "Armed Forces Americas": "AA", "DELAWARE": "DE", "ALASKA": "AK", "ILLINOIS": "IL", "Armed Forces Africa": "AE", "SOUTH DAKOTA": "SD", "CONNECTICUT": "CT", "MONTANA": "MT", "MASSACHUSETTS": "MA", "PUERTO RICO": "PR", "Armed Forces Canada": "AE", "NEW HAMPSHIRE": "NH", "MARYLAND": "MD", "NEW MEXICO": "NM", "MISSISSIPPI": "MS", "TENNESSEE": "TN", "PALAU": "PW", "COLORADO": "CO", "Armed Forces Middle East": "AE", "NEW JERSEY": "NJ", "UTAH": "UT", "MICHIGAN": "MI", "WEST VIRGINIA": "WV", "WASHINGTON": "WA", "MINNESOTA": "MN", "OREGON": "OR", "VIRGINIA": "VA", "VIRGIN ISLANDS": "VI", "MARSHALL ISLANDS": "MH", "WYOMING": "WY", "OHIO": "OH", "SOUTH CAROLINA": "SC", "INDIANA": "IN", "NEVADA": "NV", "LOUISIANA": "LA", "NORTHERN MARIANA ISLANDS": "MP", "NEBRASKA": "NE", "ARIZONA": "AZ", "WISCONSIN": "WI", "NORTH DAKOTA": "ND", "Armed Forces Europe": "AE", "PENNSYLVANIA": "PA", "OKLAHOMA": "OK", "KENTUCKY": "KY", "RHODE ISLAND": "RI", "DISTRICT OF COLUMBIA": "DC", "ARKANSAS": "AR", "MISSOURI": "MO", "TEXAS": "TX", "MAINE": "ME"}

code_to_state = {v: k.title() for k, v in state_to_code.items()}

def shorternNucleoChange(NucleoChange):
    '''
    If the NucleoChane string is too long, then remove the nucleotide after 'del' or 'ins'
    For example: c.2236_2250delGAATTAAGAGAAG  ->  c.2236_2250del
    '''
    if len(NucleoChange)>15:
        trimed_end = [m.end() for m in re.finditer("del|ins", NucleoChange)][-1]
        return NucleoChange[:trimed_end]
    else:
        return NucleoChange



def MutationsFromVCF(sample):
    '''  extract actionable mutations from VCF '''
    mutations={}
    pathogenic_mutations=[]
    for v in sample:
        if 'CLNACC' not in v.INFO and 'EFF' not in v.INFO: continue
        try:
            depth = v.samples[0]['DP'][0]
        except:
            depth = v.INFO['DP']
        if depth<min_depth: continue
        if v.QUAL<min_qual: continue
        try:
            freq = float(v.samples[0]['FREQ'].strip('%'))/100  # VarScan
        except:
            try:
                AD = v.samples[0]['AD']  # GATK
                freq = AD[1]*1.0/depth  
            except:
                freq = v.samples[0]['VF'] # somaticVariant Caller
        if freq < min_freq: continue
        
        # find the EFF record with preferred transcript
        preferred_found=False
        n_eff = 0
        while (not preferred_found) and n_eff<len(v.INFO["EFF"].split(",")):
            mutation_eff = EFF(v.INFO["EFF"].split(",")[n_eff])
            transcript = mutation_eff.Transcript_ID.split(".")[0]
            GeneName = mutation_eff.Gene_Name
            if GeneName not in preferred_transcript: break
            if transcript in preferred_transcript[GeneName]:
                preferred_found=True
            n_eff+=1

        try:
            mutation_eff.Mutation_Name
        except:
            continue

        if 'CLNACC' in v.INFO:
            variant=v.INFO["CLNACC"].split(",")[0].split(".")[0]
            try:
                mutation = mutation_translate(variant)
            except:
                continue
            if v.INFO["CLNSIG"].startswith("5") or v.INFO["CLNSIG"].startswith("255") or v.INFO["CLNSIG"].startswith("6"):
                pathogenic_mutations.append(variant+":"+mutation)
        else:
            if mutation_eff.AA_change==None: continue
        mutation=mutation_eff.Mutation_Name
        if mutation.endswith("="): continue  # bypass synonymous mutation
        Gene = mutation_eff.Gene_Name
        ''' 
        if len(v.REF)!=len(v.ALT) and Gene in ['EGFR','ERBB2']:  # check deletion or insertion on EGFR exons
            Gene = mutation_eff.Gene_Name
            Exon = str(mutation_eff.Exon_Rank)
            if len(v.REF)>len(v.ALT):
                Alt = "del"
            else:
                Alt = "ins"
            mutation = "%s-E%s_%s"%(Gene,Exon,Alt)
        '''
        mutations[mutation] = mutation_eff
    return mutations,pathogenic_mutations



def RecordString(mutation, recommendation, group_index, Type="SNV-indel", title=["Alteration Detected","Therapies"]):
    ''' print four-row record for group1,2,3 based on mutation and recomendation record  
        mutation: Gene-ProteinChange
        recommendation: [cancer_type, Drug, reference]  
        group-index: 1,2,3  
        Type: SNV-indel, Amplification, Fusion 
        Title: the title for first two lines '''
    if Type!="SNV-indel":
        Gene = mutation.split("-",1)[0]
        Alteration = Type
    else:
        Gene = mutation.split("-",1)[0]
        Alteration = mutation.split("-",1)[1]
    firstTwo = "%d\t%s"%(group_index,Gene)
    Line1 = "%s\t%s\t%s\t"%(firstTwo,title[0],Alteration)
    Line2 = "%s\t%s\t%s\t"%(firstTwo,title[1],recommendation[1])
    Line3 = "%s\tTumor Type\t%s\t"%(firstTwo,recommendation[0])
    Line4 = "%s\tReference\t%s\t"%(firstTwo,recommendation[2])
    return "\n".join([Line1,Line2,Line3,Line4])
         
        
vcf_file = args.VCFfile
File = open(vcf_file,'r')
vcf = VCFReader(File)
point_result, patho_result = MutationsFromVCF(vcf)
File.close()
updateMutationFile()  ##  from ClinAccToMutationName, update the mutation name mapping file
#print >>output,patho_result
 
sg=State_graph()    # distances between state

Total_PubMed=[]
Total_drugs=[]

table11_str=[]
table12_str=[]
table2_str=[]
table3_str=[]
Alteration_details={}
Gene_info={}
Alteration_list_positive=[]

def interpretationToLine(interp, group="therapyS"):
    lines = []
    if group=="therapyO":  # for therapy with benefits in other cancer type, the cancer type may be different for different drugs, need to list separately
        for t in interp[group].split(", "):
            lines.append([interp['therapies'][t]['disease'],t,"FDA"])
    else:    # for therapyS and therapyR, list drugs together and search for disease type with the first drug name
        t = interp[group].split(", ")[0]
        if t in interp['therapies']:
            lines.append([interp['therapies'][t]['disease'],interp[group],"FDA"])
        else:
            lines.append([patient_information['disease'],interp[group],"FDA"])
    return sorted(lines, key=lambda x:x[0])
    

Table_n = 5
for mutation in sorted(total_info.keys()):
    # alteration details
    interp = total_info[mutation]
    pathway = interp['pathway']
    summary = interp['comment']
    Gene = mutation.split("-")[0]
    firstTwo = "%d\t%s"%(Table_n,Gene)
    if "amplification" in mutation:
        Line1 = "%s\tPathways\t%s\t"%(firstTwo, pathway)
        Line2 = "%s\tAlteration Detected\t%s\t"%(firstTwo, "Amplification")
        Line3 = "%s\tVariation Type\t%s\t"%(firstTwo, "Amplification")
        Alteration_details[mutation] = [Line1,Line2,Line3]
        Type = "Amplification"
    else:
        try:
            eff = point_result[mutation]
        except: continue
        if "del" in mutation and "ins" in mutation:
            mutation_type="Indel"
        elif ("del" in mutation) or ("fs" in mutation and "del" in eff.c_change):
            mutation_type="Deletion"
        elif ("ins" in mutation) or ("fs" in mutation and "ins" in eff.c_change):
            mutation_type="Insertion"
        else:
            mutation_type=eff.Functional_Class.title()
        Line1 = "%s\tNucleotide\t%s\t"%(firstTwo, shorternNucleoChange(eff.c_change))
        Line2 = "%s\tPathways\t%s\t"%(firstTwo, pathway)
        Line3 = "%s\tAlteration Detected\t%s\t"%(firstTwo, mutation.split("-")[-1])
        Line4 = "%s\tVariation Type\t%s\t"%(firstTwo, mutation_type)
        Alteration_details[mutation] = [Line1,Line2,Line3,Line4]
        Type = "SNV-indel"
    #recommendation
    Alteration_rank_index=0
    if interp['therapyS']!=None:
        lines = interpretationToLine(interp)
        Total_drugs.extend(interp['therapyS'].split(", "))
        for line in lines:
            table11_str.append(RecordString(mutation, line, 1, Type))
            Alteration_details[mutation].append("%s\tDetails\tResponse to %s:\tPotential Clinical Benefit in %s"%(firstTwo,line[1],line[0]))
            Alteration_rank_index+=1
    if interp['therapyO']!=None:
        lines = interpretationToLine(interp,"therapyO")
        Total_drugs.extend(interp['therapyO'].split(", "))
        for line in lines:
            table12_str.append(RecordString(mutation, line, 2, Type))
            Alteration_details[mutation].append("%s\tDetails\tResponse to %s:\tPotential Clinical Benefit in %s#"%(firstTwo,line[1],line[0]))
            Alteration_rank_index+=1
    if interp['therapyR']!=None:
        lines = interpretationToLine(interp,"therapyR")
        Total_drugs.extend(interp['therapyR'].split(", "))
        for line in lines:  
            table2_str.append(RecordString(mutation, line, 3, Type))
            Alteration_details[mutation].append("%s\tDetails\tResponse to %s:\tPotential Drug Resistance in %s"%(firstTwo,line[1],line[0]))
            Alteration_rank_index+=1
    if not Alteration_details[mutation][-1].startswith("%s\tDetails"%firstTwo):  # if no clinical recommendations in Details 
        Alteration_details[mutation].append("%s\tDetails\tResponse unknown\t"%(firstTwo))
    Alteration_details[mutation].append(Alteration_rank_index)
    Location = interp['location']
    if Gene not in Gene_info:
        Gene_info[Gene]=[summary, [Location], interp['prevalence'], [interp['effect']]]
    else:
        Gene_info[Gene][1].append(Location)
        Gene_info[Gene][3].append(interp['effect'])
    Alteration_list_positive.append(mutation)

'''
fusion = open(args.fusionOutput,'r')
all_fusion_entries = []
for i in fusion.read().split("\n"):
    if i.startswith("FusionID") or i.strip()=="": continue
    isep = i.split("\t")
    if int(isep[2])>10:
        combo = [isep[9],isep[13],"%s-%s"%(isep[9],isep[13]),"%s-%s"%(isep[13],isep[9])]
        all_fusion_entries.extend(combo)
fusion_select = set(all_fusion_entries).intersection(fusion_therapy.keys())
for f in fusion_select:
    Record = fusion_therapy[f]
    for b in sorted(Record.Recommendations['benefits'],key=lambda x:x[3]):
        table1_str.append(RecordString(mutation, b, 1, Type="Fusion"))
    for l in sorted(Record.Recommendations['lack'],key=lambda x:x[3]):
        table2_str.append(RecordString(mutation, l, 2, Type="Fusion"))
    Total_PubMed.extend(Record.PubMed)
    Total_drugs.extend(Record.Drugs)
'''


## PGx Side effect results
from subprocess import Popen, PIPE
(stdout, stderr) = Popen("grep Oncology %s_clinical_action.txt | grep -v 'GO' | grep -v 'CYP3A4'"%Sample_name, shell=True, stdout=PIPE).communicate()
lines = [x.split("\t") for x in stdout.split("\n") if x.strip()!=""]
sorted_lines = sorted(lines, key=lambda k: k[4])   # sorted by alphabetic order of gene
for line in sorted_lines:
    drugs = [x.split("(")[0].strip() for x in line[2].split(":")[-1].split(", ")]
    gene = line[4]
    genotype = line[5]
    cancer_type = line[7]
    phenotype = line[6]
    if gene=="DPYD" and phenotype in ["Poor Metabolizer","Intermediate Metabolizer"]:
        side_effect = "Increased risk of severe toxicity"
    elif gene=="TPMT" and phenotype in ["Poor Metabolizer","Intermediate Metabolizer"]:
        side_effect = "Increased risk of myelosuppression"
    elif "due to " in line[3]:
        side_effect = line[3].split("due to ")[-1].replace("an ", "").capitalize()
    else:
        side_effect = line[3].capitalize()
    Total_drugs.extend(drugs)  ## add PGx Side effect drugs
    table3_str.append(RecordString(gene+"-"+genotype, [cancer_type, ", ".join(drugs)+": || "+side_effect, "PharmGKB"], 4, title=["Genotype","Therapies and Clinical Side Effects"]))



# find unique elements and keep the order
from collections import OrderedDict
Total_PubMed = list(OrderedDict.fromkeys(PMIDs))
Total_drugs = list(OrderedDict.fromkeys(Total_drugs))

print >>output, "Group\tGene\tResultColumn\tResultValue\tResultValueDetail"
for str1 in table11_str:
    print >>output, str1
if len(table11_str)==0:
    print >>output, "1\tNo medically actionable mutations were detected in this category.\t\t\t"
for str1 in table12_str:
    print >>output, str1
if len(table12_str)==0:
    print >>output, "2\tNo medically actionable mutations were detected in this category.\t\t\t"
for str2 in table2_str:
    print >>output, str2
if len(table2_str)==0:
    print >>output, "3\tNo medically actionable mutations were detected in this category.\t\t\t"

for str3 in table3_str:
    print >>output, str3
if len(table3_str)==0:
    print >>output, "3\tNo medically actionable mutations were detected in this category.\t\t\t"


Alteration_list = sorted(Alteration_details.keys(), key=lambda x: (-Alteration_details[x][-1],x))
# sort alterations based on number of recommendations
for Alt in Alteration_list:
    print Alt
    print >>output, "\n".join(Alteration_details[Alt][:-1])

Ordered_Genes = list(OrderedDict.fromkeys([x.split("-")[0] for x in Alteration_list]))

# Clinical Trials

'''
Clinical trial information to be added
'''
Table_n=6
CT_type='clinically'  # the sorted type can be switched here
for mutation in sorted(total_info):
    gene = mutation.split("-")[0]
    CTs = total_info[mutation]['ClinicalTrials']
    for CT in CTs:
        if CT['Type'] != CT_type: continue
        ID = CT['id']
        CT_instance = ClinTrials(ID)
        if len(CT_instance.US_state)==0:
            location=", ".join(list(CT['state']))
        else:
            location=", ".join([code_to_state[x] for x in sg.two_nearest(state, CT_instance.US_state)])
        cleaned_therapies=[]
        for i in CT_instance.Therapies:
            cleaned_therapies.extend(CT_instance.clean_therapy(i))
        Therapies = ", ".join(list(set(cleaned_therapies)))
        Phase = ",".join([str(x) for x in CT_instance.Phase])
        print >>output, "%d\t%s\tTherapies\t%s\t"%(Table_n,gene,Therapies.decode("ISO-8859-1"))
        print >>output, "%d\t%s\tNCT ID\t%s\t"%(Table_n,gene,ID)
        print >>output, "%d\t%s\tTitle\t%s\t"%(Table_n,gene,CT['title'])
        print >>output, "%d\t%s\tPhase\t%s\t"%(Table_n,gene,Phase)
        print >>output, "%d\t%s\tLocations#\t%s\t"%(Table_n,gene,location)



# gene mutation information
Table_n+=1
for gene in Ordered_Genes:
    geneinfo = Gene_info[gene]
    print >>output, "%d\t%s\tComment\t%s\t"%(Table_n,gene,geneinfo[0])
    print >>output, "%d\t%s\tTitle\tMutation location in gene and/or protein\t%s"%(Table_n,gene," | ".join(geneinfo[1]))
    print >>output, "%d\t%s\tTitle\tMutation prevalence\t%s"%(Table_n,gene,geneinfo[2])
    print >>output, "%d\t%s\tTitle\tEffect of mutation\t%s"%(Table_n,gene," | ".join(geneinfo[3]))

Table_n+=1
Drugs = Drugs()  # from ClinTrials.ClinTrialsUtil module, initiate the class
for drug in Total_drugs:
    Name, Link = Drugs.printInfo(drug)
    if Name!=None and Link!=None:
        print >>output, "%d\t%s\tLink\t%s\t"%(Table_n, Name.decode("ISO-8859-1"), Link)

Table_n+=1
for p in Total_PubMed:
    try:
        print >>output, "%d\t%s\t\t\t"%(Table_n, PM.PubMedToRef(p, Long=True))
    except:
        continue

Table_n+=1
for g in Guideline:
    print >>output, "%d\tGuideline\t%s\t%s\t"%(Table_n, g, Guideline[g])

Table_n+=1
print >>output, "%d\t%s"%(Table_n, "\t".join(Alteration_list_positive))

Table_n+=1
print >>output, "%d\tN-of-One\t\t\t"%(Table_n)
PM.UpdateLocalStorage()
