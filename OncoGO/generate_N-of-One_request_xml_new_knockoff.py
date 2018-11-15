from VCFmodules.VCFutility import *
import sys, codecs, subprocess, argparse, os, re
scriptFolder = os.path.dirname(os.path.abspath(sys.argv[0]))+"/"
sys.path.append(scriptFolder)
from ClinTrials.ClinTrialsUtil import *
from VCFmodules.SnpEff import *
from VCFmodules.GeneInfo import *
from datetime import timedelta, date, datetime
import lxml.etree as ET
GI = GeneInfo(local_file=scriptFolder+"/GeneInfo.txt")
PM = PubMed(local_file=scriptFolder+"/PubMed_info.txt")

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

state_to_code = {"VERMONT": "VT", "GEORGIA": "GA", "IOWA": "IA", "Armed Forces Pacific": "AP", "GUAM": "GU", "KANSAS": "KS", "FLORIDA": "FL", "AMERICAN SAMOA": "AS", "NORTH CAROLINA": "NC", "HAWAII": "HI", "NEW YORK": "NY", "CALIFORNIA": "CA", "ALABAMA": "AL", "IDAHO": "ID", "FEDERATED STATES OF MICRONESIA": "FM", "Armed Forces Americas": "AA", "DELAWARE": "DE", "ALASKA": "AK", "ILLINOIS": "IL", "Armed Forces Africa": "AE", "SOUTH DAKOTA": "SD", "CONNECTICUT": "CT", "MONTANA": "MT", "MASSACHUSETTS": "MA", "PUERTO RICO": "PR", "Armed Forces Canada": "AE", "NEW HAMPSHIRE": "NH", "MARYLAND": "MD", "NEW MEXICO": "NM", "MISSISSIPPI": "MS", "TENNESSEE": "TN", "PALAU": "PW", "COLORADO": "CO", "Armed Forces Middle East": "AE", "NEW JERSEY": "NJ", "UTAH": "UT", "MICHIGAN": "MI", "WEST VIRGINIA": "WV", "WASHINGTON": "WA", "MINNESOTA": "MN", "OREGON": "OR", "VIRGINIA": "VA", "VIRGIN ISLANDS": "VI", "MARSHALL ISLANDS": "MH", "WYOMING": "WY", "OHIO": "OH", "SOUTH CAROLINA": "SC", "INDIANA": "IN", "NEVADA": "NV", "LOUISIANA": "LA", "NORTHERN MARIANA ISLANDS": "MP", "NEBRASKA": "NE", "ARIZONA": "AZ", "WISCONSIN": "WI", "NORTH DAKOTA": "ND", "Armed Forces Europe": "AE", "PENNSYLVANIA": "PA", "OKLAHOMA": "OK", "KENTUCKY": "KY", "RHODE ISLAND": "RI", "DISTRICT OF COLUMBIA": "DC", "ARKANSAS": "AR", "MISSOURI": "MO", "TEXAS": "TX", "MAINE": "ME"}

code_to_state = {v: k for k, v in state_to_code.items()}

f = open(scriptFolder+"N-of-One_polymorphisms.txt")
polymorphisms = f.read().strip().split("\n")


def ParseArg():
    p = argparse.ArgumentParser(description="generate OncoGxOne interpretation file with clinvar annotated VCF file, coverage file, fusionmap output and mutation/drug information", epilog="Need: VCFutility")
    p.add_argument("VCFfile",type=str, help="clinvar annotated VCF file")
    p.add_argument("fusionOutput",type=str, help="fusionmap output")
    p.add_argument("CNV",type=str, help="CNV output file")
    p.add_argument("-s",'--snomed',type=str, required=True, help="Patient's SNOMED code within N-of-One's list")
    p.add_argument("-D", "--DOB", type=str, required=True, help="Patient's date of birth, in the format of '%%m/%%d/%%Y'")
    p.add_argument("-S", "--State", type=str, required=True, help="Patient's location state")
    p.add_argument("-g", "--gender", type=str, required=True, help="Patient's gender information, select from 'Male/Female'")
    p.add_argument('-t','--therapy',type=str,default="/home/pengfei.yu/OncoGxOne/pipeline/OncoGxOne_knowledgebase_main_20160512.txt",help="mutation to therapy database file, default: OncoGxOne_knowledgebase_main_20160512.txt")
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
output = open(args.output,'w')#,encoding='utf-8')
#output = sys.stdout
population_freq_cut = 0.05

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


def MutationsFromVCF(sample,point_therapy):
    '''  extract actionable mutations from VCF '''
    mutations={}
    pathogenic_mutations=[]
    for v in sample:
        if 'dbNSFP_COSMIC_ID' in v.INFO:
            COSMIC_ID = v.INFO['dbNSFP_COSMIC_ID']
        else:
            COSMIC_ID = ""
		## yifei: knock off fliter
       ## if 'CLNACC' not in v.INFO and 'EFF' not in v.INFO: continue
       ## if v.FILTER!="PASS": continue
        try:
            depth = v.samples[0]['DP'][0]
        except:
            depth = v.INFO['DP']
       ## if depth<min_depth: continue
       ## if v.QUAL<min_qual: continue
        try:
            freq = float(v.samples[0]['FREQ'].strip('%'))/100  # VarScan
        except:
            try:
                AD = v.samples[0]['AD']  # GATK
                freq = AD[1]*1.0/depth  
            except:
                freq = v.samples[0]['VF'] # somaticVariant Caller
        ## if freq < min_freq: continue  # ignore the variants with low allele frequency 

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
            popu_freq = v.INFO["dbNSFP_1000Gp1_AF"]
        except:
            popu_freq = 0.0
        try:
            mutation_eff.Mutation_Name
        except:
            continue
        ClnSig_list = []
        if "CLNSIG" in v.INFO:
            ClnSig_list =  [j for x in v.INFO["CLNSIG"].split(",") for j in x.split("|")]
        ## yfiei: turn off fliter
		## if "5" not in ClnSig_list and 'dbNSFP_COSMIC_ID' not in v.INFO and mutation_eff.Effect_Impact!="HIGH":
            ## continue
        ## if mutation_eff.Mutation_Name in polymorphisms: continue # if it is normal polymorphism
        ##if popu_freq>population_freq_cut and mutation_eff.Mutation_Name not in point_therapy: continue  # ignore the variants with high population frequency and not in our knowledgebase
        #if mutation_eff.Effect_Impact=="LOW": continue
        print mutation_eff.AA_change, mutation_eff.Mutation_Name, v.ALT, v.REF
        if len(v.REF)>len(v.ALT): ## the mutation name (position) will be a range if the variant is deletion
            position = "%s:%d-%d"%(v.CHROM, v.POS+len(v.ALT), v.POS+len(v.REF)-1)
        else:
            position = "%s:%d"%(v.CHROM,v.POS)
        mutations[position] = [mutation_eff,COSMIC_ID, popu_freq]
    return mutations

class KnowledgeRecord():
    '''
    convert mutation ("gene-mutation") in Knowledgebase into a object with attribute of .PubMed, .Recommendations, .Drugs, ...
    '''
    def __init__(self, mType):
        self.Recommendations={}
        self.Recommendations['benefits']=[]
        self.shortRecommendation=[]
        self.Recommendations['lack']=[]
        self.Drugs=[]
        self.PubMed=[]
        self.Location=""
        self.Type=mType
        self.Frequency={}
        self.cancer_type=""
    def addLineRecord(self, line):
        '''
        line: the Knowledgebase line: Gene | mutation | mutation type | cancer type | frequency | potential benefits | lack of benefits | location
        '''
        lsep = line.strip().split("\t")
        if self.Location!="": self.Location=lsep[7]
        assert(self.Type==lsep[2])  # assert the mutation is the same
        self.cancer_type = lsep[3]
        self.Frequency[self.cancer_type]=lsep[4]
        if (lsep[5]=="" or lsep[5]==".") and (lsep[6]=="" or lsep[6]=="."): return
        benefits = lsep[5].split(", ")
        for b in benefits:
            self.addRecommendation(b)
        self.addShortRecommendation()
        lacks = lsep[6].split(", ")
        for l in lacks:
            self.addRecommendation(l, benefit=False)
        self.addShortRecommendation(benefit=False)
    def addRecommendation(self,recomRecord,benefit=True):
        '''
        recomRecord example: "Crizotinib,Ceritinib(FDA)", "Tanespimycin(21502504|22277784)", "Dabrafenib+Trametinib(FDA)" 
        benefit: True -- with benefits; False -- lack of benefits
        '''
        if recomRecord=="": return
        tmp = re.match(r'(.+)\((.+)\)', recomRecord, re.M)
        if tmp:
            drugs = tmp.group(1)
            PubMeds = tmp.group(2).split("|")
            for p in PubMeds:
                if p not in ['FDA','COSMIC']:
                    self.PubMed.append(p)
        else:
            drugs = recomRecord
            PubMeds=[]
        self.Drugs.extend(re.split(',|\+',drugs))
        shortDescription = ", ".join(PM.PubMedToRef(x) for x in PubMeds)
        if benefit==True:
            self.Recommendations['benefits'].append([self.cancer_type, drugs, shortDescription])
        else:
            self.Recommendations['lack'].append([self.cancer_type, drugs, shortDescription])
    def addShortRecommendation(self,benefit=True):
        ''' short recommendation is used in the Alteration Details table, only one line for each cancer type '''
        if benefit:
            string = "benefits"
            effect = "Increased"
        else:
            string = "lack"
            effect = "Decreased"
        drugs_sameCancer = []
        for b in self.Recommendations[string]:
            if self.cancer_type==b[0]:
                drugs_sameCancer.append(b[1])
        if len(drugs_sameCancer)!=0:
            self.shortRecommendation.append("Response to "+",".join(drugs_sameCancer)+":\t%s efficacy in %s"%(effect,self.cancer_type))


therapy = open(args.therapy,'r')
point_therapy=[]
CNV_therapy={}
fusion_therapy={}
for t in therapy:
    if t.strip()=="": continue
    tsep = t.split("\t")
    if tsep[2] in ["point","indel"]:
        name = "%s-%s"%(tsep[0],tsep[1])
        if name not in point_therapy:
            point_therapy.append(name)
    if tsep[2]=="fusion":
        if "-" in tsep[1]:
            name = tsep[1]
        else:
            name = tsep[0]
        if name not in fusion_therapy:
            fusion_therapy[name] = KnowledgeRecord(tsep[2])
        fusion_therapy[name].addLineRecord(t)
    if tsep[2]=="amplification":
        name = tsep[0]
        if name not in CNV_therapy:
            CNV_therapy[name] = KnowledgeRecord(tsep[2])
        CNV_therapy[name].addLineRecord(t)


vcf_file = args.VCFfile
File = open(vcf_file,'r')
vcf = VCFReader(File)
point_result = MutationsFromVCF(vcf, point_therapy)
File.close()
patientID = vcf_file.split("/")[-1].split("_")[0]
reportID = patientID+datetime.now().strftime('-%m%d%Y%H%M')
DOB = datetime.strptime(args.DOB,'%m/%d/%Y').date()
age=int((date.today()-DOB).days/365.25)
gender=args.gender.lower()
state=args.State
Country = "US"
snomedID = args.snomed

if state in code_to_state:
    state=code_to_state[state].title()

report_request = ET.Element("report-request", nsmap={"xsi":"http://www.w3.org/2001/XMLSchema-instance"})
report_request.set("product-key","f3665ee0-51a4-49df-bbd4-9724225bb6e2")
report_request.set("report-id",reportID)
report_request.set("customer-id","573f63f3-fcff-4310-bb4a-646da0af67e8")
report_request.set("snomed-disease-concept-id",snomedID)
report_request.set("schema-version","1.0.6.4")
patient = ET.SubElement(report_request, "patient")
patient.set("patient-id",patientID)
ET.SubElement(patient, "age").text = str(age)
ET.SubElement(patient, "gender").text = gender
ET.SubElement(patient, "state-province").text = state
ET.SubElement(patient, "country-code").text = Country
test_results = ET.SubElement(report_request, "test-results")

for i in point_result:
    if point_result[i][0].Gene_Name in ["CYP2D6","XRCC1","DPYD","TPMT","UGT1A1","CYP2C8","MTHFR","TYMS"]: continue
    record = ET.SubElement(test_results,"sequencing-test-result",
			gene=point_result[i][0].Gene_Name,platform="Illumina MiSeq",result="positive")
    record.set("sequencing-method","seq")
    record.set("protein-change",point_result[i][0].Mutation_Name.split("-")[-1])
    record.set("map-location",i)
    record.set("coding-seq-change",point_result[i][0].c_change.replace("&gt;",">"))
    record.set("transcript-id",point_result[i][0].Transcript_ID.split(".")[0])
    record.set("variant-type","short-variant")
    if point_result[i][1]!="":   # add COSMIC ID if there is annotation for COSMIC
        record.set("cosmic-id",point_result[i][1])


fusion = open(args.fusionOutput,'r')
all_fusion_entries = []
for i in fusion.read().split("\n"):
    if i.startswith("Est_Type") or i.strip()=="": continue
    isep = i.split("\t")
    if int(isep[12])>=10:
        Gene1 = isep[1]
        Gene2 = isep[2]
        combo = [Gene1,Gene2,"%s-%s"%(Gene1,Gene2),"%s-%s"%(Gene2,Gene1)]
        record = ET.SubElement(test_results,"sequencing-test-result",
                        gene=Gene2, platform="Illumina MiSeq",result="positive")
        record.set("sequencing-method","seq")
        record.set("protein-change","%s-%s fusion"%(Gene1,Gene2))
        record.set("variant-type","rearrangement")
        record.set("comment","%s(%s)-%s(%s)"%(Gene1,isep[3],Gene2,isep[4]))
        all_fusion_entries.extend(combo)

CNV_file = open(args.CNV,'r')
Sample_name = args.CNV.split("_CNV")[0]
CNV_result = [x.split("\t")[0].strip() for x in CNV_file.read().split("\n")]
CNV_select = set(CNV_result).intersection(CNV_therapy.keys())
for Gene in CNV_select:
    transcript = preferred_transcript[Gene][0]
    record = ET.SubElement(test_results,"sequencing-test-result",
                        gene=Gene, platform="Illumina MiSeq",result="positive")
    record.set("sequencing-method","seq")
    record.set("protein-change","amplification")
    record.set("transcript-id",transcript)
    record.set("variant-type","copy-number")

tree = ET.ElementTree(report_request)
print >>output, ET.tostring(report_request, pretty_print=True)
