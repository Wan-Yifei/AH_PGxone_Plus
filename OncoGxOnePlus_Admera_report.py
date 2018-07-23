#!/usr/bin/env python
#coding:utf-8 
from reportlab.platypus import *
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch,mm
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from datetime import timedelta, date, datetime
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, toColor
#from VCFutility import * 
from ClinTrials.ClinTrialsUtil import *
import sys, codecs, os, argparse,re, pprint

import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
scriptFolder = os.path.dirname(os.path.abspath(sys.argv[0]))+"/"
pdfmetrics.registerFont(TTFont('Calibri', scriptFolder+'./fonts/Calibri.ttf'))
pdfmetrics.registerFont(TTFont('Calibri-Bold', scriptFolder+'./fonts/Calibri-Bold.ttf'))

state_to_code = {"JIANGSU":'Jiangsu',"VERMONT": "VT", "GEORGIA": "GA", "IOWA": "IA", "Armed Forces Pacific": "AP", "GUAM": "GU", "KANSAS": "KS", "FLORIDA": "FL", "AMERICAN SAMOA": "AS", "NORTH CAROLINA": "NC", "HAWAII": "HI", "NEW YORK": "NY", "CALIFORNIA": "CA", "ALABAMA": "AL", "IDAHO": "ID", "FEDERATED STATES OF MICRONESIA": "FM", "Armed Forces Americas": "AA", "DELAWARE": "DE", "ALASKA": "AK", "ILLINOIS": "IL", "Armed Forces Africa": "AE", "SOUTH DAKOTA": "SD", "CONNECTICUT": "CT", "MONTANA": "MT", "MASSACHUSETTS": "MA", "PUERTO RICO": "PR", "Armed Forces Canada": "AE", "NEW HAMPSHIRE": "NH", "MARYLAND": "MD", "NEW MEXICO": "NM", "MISSISSIPPI": "MS", "TENNESSEE": "TN", "PALAU": "PW", "COLORADO": "CO", "Armed Forces Middle East": "AE", "NEW JERSEY": "NJ", "UTAH": "UT", "MICHIGAN": "MI", "WEST VIRGINIA": "WV", "WASHINGTON": "WA", "MINNESOTA": "MN", "OREGON": "OR", "VIRGINIA": "VA", "VIRGIN ISLANDS": "VI", "MARSHALL ISLANDS": "MH", "WYOMING": "WY", "OHIO": "OH", "SOUTH CAROLINA": "SC", "INDIANA": "IN", "NEVADA": "NV", "LOUISIANA": "LA", "NORTHERN MARIANA ISLANDS": "MP", "NEBRASKA": "NE", "ARIZONA": "AZ", "WISCONSIN": "WI", "NORTH DAKOTA": "ND", "Armed Forces Europe": "AE", "PENNSYLVANIA": "PA", "OKLAHOMA": "OK", "KENTUCKY": "KY", "RHODE ISLAND": "RI", "DISTRICT OF COLUMBIA": "DC", "ARKANSAS": "AR", "MISSOURI": "MO", "TEXAS": "TX", "MAINE": "ME"}

code_to_state = {v: k for k, v in state_to_code.items()}


def ParseArg():
    p=argparse.ArgumentParser( description = 'generate report for OncoGxOnePlus Admera genetic test')
    p.add_argument('input',type=str,help="input file with all information to generate report, *_interpretation.txt")
    p.add_argument('-o', '--outputPDF', type=str, help="output pdf file")
    p.add_argument('-c','--condition', type=str, default="Not applicable", help="patient condition, to be added in 'Cancer type' section), default: Not applicable")
    p.add_argument("-p","--pName",type=str, help="Patient name", default=" ")
    p.add_argument("-s","--sampleDate",type=str, help="Sample date, format: '%%b %%d, %%Y'/'%%m/%%d/%%Y'",default="12/29/2016")
    p.add_argument("-P","--PhName",type=str, help="Physician name",default=" ")
    p.add_argument("-i","--ID",type=str, help="Patient ID", default=" ")
    p.add_argument("-S","--Source",type=str, help="Sample source", default="FFPE Slides")
    p.add_argument("-a","--address",type=str, help="Address", default="")
    p.add_argument("-g","--gender",type=str, help="Gender of patient", default="")
    p.add_argument("-I","--Institute", type=str, help="Institute",default="")
    p.add_argument("-D","--DOB", type=str, help="Date of birth for patient, format: '%%b %%d, %%Y'/'%%m-%%d-%%Y'", default="")
    p.add_argument("-A","--Age",type=str, help="Age of the patient", default="")
    if len(sys.argv)==1:
        print >> sys.stderr, p.print_help()
        sys.exit(0)
    return p.parse_args()


#input
args = ParseArg()
InputFile = args.input
PatientName = args.pName
ReportDate = date.today()
try:
    SampleDate = datetime.strptime(args.sampleDate,'%b %d, %Y').date()
except:
    try:
        SampleDate = datetime.strptime(args.sampleDate,'%m/%d/%Y').date()
    except:
        pass
try:
    DOB = datetime.strptime(args.DOB,'%b %d, %Y').date()
except:
    try:
        DOB = datetime.strptime(args.DOB,'%m-%d-%Y').date()
    except:
        pass
Institution = args.Institute

try:
    Age = str(int((ReportDate-DOB).days/365.25))
except:
    Age = args.Age
Sex = args.gender
ID = args.ID
PatientAddress = args.address
try:
    PhysicianAddress = Info.orderPhysician['Address']+"<br />"+"%s, %s, %s"%(Info.orderPhysician['City'],state_to_code[Info.orderPhysician['State'].upper()],Info.orderPhysician['Zip'])
except:
    PhysicianAddress = args.address
Source = args.Source
Accession = args.ID
action_file = codecs.open(InputFile,'r',encoding='utf-8')  #'iso8859-1')
pdf_file = args.outputPDF
condition = args.condition

# ICD10 description generation 
from pymedtermino.icd10 import *
def icd_description(code):
    if code=="C80.1":
        return "C80.1: Malignant (primary) neoplasm, unspecified"
    if code=="C80.0":
        return "C80.0: Disseminated malignant neoplasm, unspecified"
    if code=="C67.9 & C65.9":
	return "C67.9 & C65.9: Malignant neoplasm of bladder, unspecified & Malignant neoplasm of unspecified renal pelvis"
    if code=="I26.99; K76.9; I82.401":
	return "I26.99; K76.9; I82.401: Other pulmonary embolism without acute cor pulmonale; Liver disease, unspecified; Acute embolism and thrombosis of unspecified deep veins of right lower extremity"
    if code=="C34.11":
	return "C34.11: Malignant neoplasm of upper lobe, right bronchus or lung"
    if code=="C53.9":
        return "C53.9: Malignant neoplasm of Cervix uteri, unspecified"
    if code=="C77.9":
        return "C77.9: Secondary and unspecified malignant neoplasm: Lymph node, unspecified"
    if code=="C25.9":
        return "C25.9: Malignant neoplasm of pancreas, unspecified"
    if code=="C79.31":
        return "C79.31: Secondary malignant neoplasm of brain"
    if code=="C34.12":
        return "C34.12: Malignant neoplasm of upper lobe, left bronchus or lung"
    return "%s: %s"%(code,ICDtoDescription(code,ICD10=True)[1])



if not os.path.exists(scriptFolder+"OncoGxOnePlus_gene_list.txt"):
    print "Please put the OncoGxOnePlus_gene_list file in the same folder with the program"
    sys.exit(0)

PAGE_HEIGHT=defaultPageSize[1]
styles = getSampleStyleSheet()
HeaderStyle = styles["Heading1"]
ParaStyle = styles["Normal"]
PreStyle = styles["Code"]
StylePT = styles["BodyText"] # paragraph style for paragraph in table
StylePT.wordWrap="CJK" # allow long word wrap http://stackoverflow.com/questions/11839697/wrap-text-is-not-working-with-reportlab-simpledoctemplate

def myFirstPage(canvas,doc):
    canvas.saveState()
    canvas.drawImage(PythonImage(scriptFolder+"./img/OncoGx_panel_background_2.jpg"),19*mm,25*mm,175*mm,160*mm)
    canvas.setStrokeColorRGB(0.33,0.61,0.75)
    canvas.line(15*mm,255*mm,200*mm,255*mm)
    canvas.restoreState()


def myLaterPage(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColorRGB(0.33,0.61,0.75)
    canvas.line(15*mm,255*mm,200*mm,255*mm)
    canvas.restoreState()


def CTfirstPage(canvas,doc):
    canvas.saveState()
    canvas.drawImage(scriptFolder+"./img/admera_health_final_logo.jpg",13*mm, 255*mm, 45*mm, 22*mm)
    canvas.setFont("Helvetica", 13)
    canvas.drawRightString(200*mm, 270*mm, "Admera Health, LLC")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(200*mm, 264*mm, "126 Corporate Boulevard • South Plainfield, NJ 07080")
    canvas.drawRightString(200*mm, 259*mm, "+1-908-222-0533 • ClientCare@admerahealth.com")
    canvas.setStrokeColorRGB(0.33,0.61,0.75)
    canvas.line(15*mm,252*mm,200*mm,252*mm)
    canvas.restoreState()


def PythonImage(png):
    jpg = png.replace("png","jpg")
    if not os.path.exists(jpg):
        tmp = open(png)
        f = open(png.replace("png","jpg"),'w')
        f.write(tmp.read())
        f.close()
        tmp.close()
    return jpg


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.drawImage(scriptFolder+"./img/admera_health_final_logo.jpg",13*mm, 256*mm, 45*mm, 22*mm)
        #self.setFont("Helvetica", 13)
        #self.drawRightString(200*mm, 270*mm, "Admera Med-tech Co. Ltd.")
        #self.setFont("Helvetica", 8)
        #self.drawRightString(200*mm, 264*mm, "218 Xinghu Road• Suzhou, China 215123")
        #self.drawRightString(200*mm, 259*mm, "+86-512-62628766 • Customerservice@admerahealth.com.cn")
        self.setFont("Helvetica", 6)
        self.drawString(10*mm,15*mm,("OncoGxOne\xe2\x84\xa2 Plus Report for %s"%(PatientName)).decode('utf-8'))
        #self.drawCentredString(115*mm,15*mm,"Laboratory Director: James Dermody, PhD | CLIS ID: 0005783 | CLIA ID: 31D2038676")
        self.drawRightString(200*mm,15*mm,"Rev1")
        self.setFont("Helvetica", 8)
        self.drawRightString(200*mm, 10*mm,
            "Page %d of %d" % (self._pageNumber, page_count))
 
def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.1, *args, **kwargs):
    s = Spacer(0.2*inch, sep*inch)
    para = klass(txt, style=style, *args, **kwargs)
    sect = [s, para]
    result = KeepTogether(sect)
    return result
 
def p(txt):
    return header(txt, style=ParaStyle, sep=0.1)
 
def pre(txt):
    s = Spacer(0.1*inch, 0.1*inch)
    p = Preformatted(txt, PreStyle)
    precomps = [s,p]
    result = KeepTogether(precomps)
    return result
 
def go():
    doc = BaseDocTemplate(pdf_file, pagesize = letter)
    doc.addPageTemplates([PageTemplate("First",[Frame(14*mm,17*mm,187*mm,240*mm)],onPage=myFirstPage),
                          PageTemplate("Later",[Frame(14*mm,17*mm,187*mm,238*mm)],onPage=myLaterPage),
                          PageTemplate("CTfirst",[Frame(14*mm,17*mm,187*mm,235*mm)],onPage=CTfirstPage),
                        ])
    doc.build(Elements, canvasmaker=NumberedCanvas)
    os.system("pdfunite %s/img/OncoGxOne_Plus_Front_v2.2.pdf %s %s/img/OncoGxOne_Plus_Back_v2.2.pdf temp.pdf"%(scriptFolder, pdf_file, scriptFolder))
    os.system("mv temp.pdf %s"%pdf_file)


def shorternNucleoChange(NucleoChange):
    '''
    If the NucleoChane string is too long, then remove the nucleotide after 'del' or 'ins'
    For example: c.2236_2250delGAATTAAGAGAAG  ->  c.2236_2250del
    '''
    if len(NucleoChange)>20:
        trimed_end = [m.end() for m in re.finditer("del|ins", NucleoChange)][-1]
        return NucleoChange[:trimed_end]
    else:
        return NucleoChange


# parse the action file and store information in different variables
def ParseActionFile(action_file):
    '''
    ClinBenefits   # group 1
    LackClinBenefits   # group 2
    SideEffect   # group 3
    MutDetail   # group 4
    ClinTrial   # group 5
    GeneInfo   # group 6
    DrugInfo   # group 7
    Reference   # group 8
    '''
    # Group 1 - 8
    result={}
    Groups = ["ClinBenefitsSame","ClinBenefitsDiff","LackClinBenefits","SideEffect", "MutDetail","ClinTrial","GeneInfo","DrugInfo","Reference","Guideline","Alteration_list","HLAtyping", "TMB"]
    for i in [0,1,2,3,4,6,7,8,9,10,11,12]:
        result[Groups[i]] = []
    result['ClinTrial'] = {}
    n = 0 # record the line number in action file, reset when group number changes
    prev_group = 0  # record the previous group number, help to find whether to reset n 
    prev_gene = "None" # record the previous gene name, help to find whether to reset n
    Title = []  # store title for each table
    record = []  # store the row record of each table
    Genes = []  # store the order of genes
    muDetail_n=-1 # number of mutation detail table
    geneMut_n=-1 # number of gene detail seqction
    for l in action_file.read().split("\n"):
        if l.startswith("Group") or l.strip()=="": continue # skip the first line
        lsep = l.strip().split("\t")
        group=int(lsep[0])
        if group!=prev_group or (lsep[1]!=prev_gene and group in [5,6,7]):  # when group changes
            n=0
            Title = []
        n+=1
        if group<5:
            if len(lsep)<3:
                if group<4:
                    result[Groups[group-1]].append(["Gene","Alteration Detected","Therapies","Tumor Type","Reference"])
                elif group==4:
                    result[Groups[group-1]].append(["Gene","Genotype","Therapies and Clinical Side Effects","Tumor Type","Reference"])
                result[Groups[group-1]].append(["No medically actionable mutations were detected in this category.","","",""])
            else:
                record.append(lsep[3])
                if n<=4:
                    Title.append(lsep[2])
                if n%4==0:
                    if n==4:
                        Title.insert(0,"Gene")
                        result[Groups[group-1]].append(Title)
                    record.insert(0,lsep[1])
                    result[Groups[group-1]].append(record)
                    record=[]
        elif group==5:
            if lsep[2]=="Nucleotide":
                muDetail_n+=1
                result[Groups[group-1]].append("")
                Gene_title = Paragraph("<font color='#ffc000'><b><u><i>%s</i></u></b></font>"%lsep[1],ParaStyle)
                Gene_cell = Paragraph("<font color='#ffffff'><b>Gene: <i>%s</i></b></font>"%lsep[1],ParaStyle)
                result[Groups[group-1]][muDetail_n]=[[Gene_title,"",""],[Gene_cell,"Nucleotide: %s"%shorternNucleoChange(lsep[3]),""],["","",""]]  # create first three row of alteration details table
            elif lsep[2]=="Pathways":
                try:
                    current_line_num = len(result[Groups[group-1]][muDetail_n])
                except:
                    current_line_num = 0
                if current_line_num==3:
                    result[Groups[group-1]][muDetail_n][1][2]="Pathways: %s"%lsep[3]  # add pathway information
                else:    # if Pathway is the first line for this alteration, for Amplification or Fusion
                    muDetail_n+=1
                    assert len(result[Groups[group-1]])==muDetail_n  # confirm the current index is correct
                    result[Groups[group-1]].append("")
                    Gene_title = Paragraph("<font color='#ffc000'><b><u><i>%s</i></u></b></font>"%lsep[1],ParaStyle)
                    Gene_cell = Paragraph("<font color='#ffffff'><b>Gene: <i>%s</i></b></font>"%lsep[1],ParaStyle)
                    result[Groups[group-1]][muDetail_n]=[[Gene_title,"",""],[Gene_cell,"","Pathways: %s"%lsep[3]],["","",""]]  # create first three row of alteration details table
            elif lsep[2]=="Alteration Detected":
                result[Groups[group-1]][muDetail_n][2][0]="Alteration Detected: %s"%lsep[3]
            elif lsep[2]=="Variation Type":
                result[Groups[group-1]][muDetail_n][2][2]="Variation Type: %s"%lsep[3]
            else:  # Details
                if len(lsep)<5: # no response
                    response = ""
                elif lsep[4].startswith("Increased") or lsep[4].startswith("Potential Clinical Benefit"):  # green color
                    if lsep[4].endswith("#"):    # different cancer type benefit
                        response = Paragraph("<font color='#0067b1'><b>%s</b></font>"%lsep[4].replace("#",""),ParagraphStyle(name = 'Normal', leftIndent=15), bulletText="\xe2\x9e\xa2")
                    else:    # same cancer type benefit
                        response = Paragraph("<font color='#238943'><b>%s</b></font>"%lsep[4],ParagraphStyle(name = 'Normal', leftIndent=15), bulletText="\xe2\x9e\xa2")
                else:  # red color
                    response = Paragraph("<font color='#d89234'><b>%s</b></font>"%lsep[4],ParagraphStyle(name = 'Normal', leftIndent=15), bulletText="\xe2\x9e\xa2")
                result[Groups[group-1]][muDetail_n].append([Paragraph('<b>%s</b>'%lsep[3],ParaStyle),"",response])    
        elif group==6:
            record.append(lsep[3])
            if n<=5:
                Title.append(lsep[2])
            if n%5==0:
                if lsep[1] not in result[Groups[group-1]]:
                    Genes.append(lsep[1])
                    result[Groups[group-1]][lsep[1]]=[]
                if n==5:
                    result[Groups[group-1]][lsep[1]].append(Title)
                result[Groups[group-1]][lsep[1]].append(record)
                record=[]
        elif group==7:
            if lsep[2]=="Comment":
                geneMut_n+=1
                result[Groups[group-1]].append({})
                result[Groups[group-1]][geneMut_n]["Comment"]=lsep[3]
                result[Groups[group-1]][geneMut_n]['Gene']=lsep[1]
            else:
                result[Groups[group-1]][geneMut_n][lsep[3]]=lsep[4]
        elif group==8:
            result[Groups[group-1]].append([lsep[1],lsep[3]])
        elif group==9:
            result[Groups[group-1]].append(lsep[1])
        elif group==10:
            result[Groups[group-1]].append(lsep[2:4])
        elif group==11:
            if len(lsep)>1:
                result[Groups[group-1]].extend(lsep[1:])
        elif group==12:
            result[Groups[group-1]].append(lsep[1:4])
        elif group==13:
            result[Groups[group-1]] = lsep[1:3]
        prev_group=group
        if group < 11:
            prev_gene=lsep[1]
   
    return result, Genes

            
        

# stripe background tables
def stripe_table(data, title, color, image, firstCT=False, sep=0.4):
    ''' Create table and title for each type of mutations 
          color: hex color for the title line
          image: image for the first cell in the table
          firstCT: whether it is the first table of clinical trials
          sep: spacer on top        '''
    ParaStyle=ParagraphStyle("Normal", alignment=TA_CENTER)
    Title_num=1+int(firstCT)  # number of tows for titles
    firstRowFontColor = "#ffffff"
    headerRowBgColor = '#404040'
    if color == '#ffffff':   # for side effect table
        firstRowFontColor = "#000000"  
        headerRowBgColor = "#7f7f7f"
    tableStyle = [
                 ('GRID',(0,Title_num),(-1,-1),1,"#afafaf"),
                 ('BACKGROUND',(0,0),(-1,0),colors.HexColor(color)),
                 ('BACKGROUND',(0,Title_num),(-1,Title_num),colors.HexColor(headerRowBgColor)),
                 ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor(firstRowFontColor)),
                 ('TEXTCOLOR',(0,Title_num),(-1,Title_num),colors.HexColor('#ffc000')),
                 ('TEXTCOLOR',(0,Title_num+1),(-1,-1),colors.HexColor('#000000')),
                 ('FONTSIZE',(0,0),(-1,-1),10),
                 ('FONT',(0,0),(-1,Title_num),'Helvetica-Bold'),
                 ('VALIGN',(0,0),(-1,-1),"MIDDLE"),
                 ('ALIGN',(0,0),(-1,Title_num),"CENTER"),
                 ]
    if title.endswith("Trials"):
        subtitle = [""]*len(data[0])
        subtitle[0] = title+"    "
        data.insert(0, subtitle)
        colWidths=[32*mm, 30*mm, 80*mm, 15*mm, 30*mm]
        tableStyle.extend([('ALIGN',(0,Title_num+1),(0,-1),"LEFT"),
                           ('ALIGN',(2,Title_num+1),(2,-1),"LEFT"),
                           ('ALIGN',(4,Title_num+1),(4,-1),"LEFT"),
                           ('SPAN',(0,Title_num-1),(-1,Title_num-1)),
                           ('BACKGROUND',(0,Title_num-1),(-1,Title_num-1),colors.HexColor("#af97d9")),
                           ('TEXTCOLOR',(0,Title_num-1),(-1,Title_num-1),colors.HexColor('#000000')),])
    elif title.endswith("Detected"):
        colWidths=[19*mm, 84*mm, 84*mm]
    elif title.startswith("Tumor Mutation"):
        colWidths=[19*mm, 149*mm, 19*mm]
        tableStyle.extend([('GRID',(0,Title_num),(-1,-1),1,"#ffffff"),
            ('GRID',(1,Title_num),(-2,-1),1,"#afafaf"),
            ('BACKGROUND',(0,Title_num),(-1,Title_num),colors.HexColor('#ffffff')),
            ('BACKGROUND',(1,Title_num),(-2,Title_num),colors.HexColor(headerRowBgColor)),
            ])
    else:
        colWidths=[19*mm, 36*mm, 60*mm, 36*mm, 36*mm]
    if firstCT or not title.endswith("Trials"):
        Title_row = [""]*len(data[0])
        Title_row[1] = title.upper()
        if firstCT:
            Title_row[1] = "CLINICAL TRIALS TO CONSIDER    "
        Title_row[0] = Image(PythonImage(scriptFolder+'./img/'+image),width = 11.5*mm, height = 11.5*mm)
        data.insert(0, Title_row)
        tableStyle.extend([('SPAN',(1,0),(-1-int(firstCT),0)),('ALIGN',(0,0),(0,0),"LEFT"),('FONTSIZE',(1,0),(-1,0),12)])
        if color == '#ffffff':  # for side effect table
            tableStyle.append(('ALIGN',(0,0),(-1,0),"LEFT"))
    if data[-1][1]=="":
        tableStyle.append(('SPAN',(0,-1),(-1,-1)))
        data[-1][0] = Paragraph("<font size=10><b><i>%s</i></b></font>"%data[-1][0],ParaStyle)
    else: 
        for i in range(Title_num+1,len(data)):
            for j in range(len(data[i])):
                if data[i][j].startswith("NCT"):
                    data[i][j] = Paragraph("<font size=10><link href='https://clinicaltrials.gov/ct2/show/%s' color='#4f81bd'><u>%s</u></link></font>"%(data[i][j],data[i][j]),ParaStyle)
                elif j==0 and data[1][0]=="Gene":
                    data[i][j] = Paragraph("<font size=10><i>%s</i></font>"%data[i][j],ParaStyle)  # gene name need to be italic
                elif data[1][j] in ["Therapies","Title","Locations#"] and title.endswith("Trials"):
                    data[i][j] = Paragraph("<font size=10>%s</font>"%data[i][j],ParagraphStyle("Normal")) # don't align center for these columns in CT table
                else:
                    data[i][j] = Paragraph("<font size=10>%s</font>"%data[i][j].replace("||","<br /><br />"),ParaStyle)  # change type to paragraph so that it can be wrapped.
    StripeTable = Table(data, style = tableStyle, repeatRows=2, colWidths=colWidths)
    sect = [Spacer(0.2*inch, sep*inch), StripeTable]
    result_table = KeepTogether(sect)
    return result_table


Elements=[NextPageTemplate(["Later","*","Later"]),]
try:
    action_file = codecs.open(InputFile,'r',encoding='utf-8')  #'iso8859-1')
    result, Genes = ParseActionFile(action_file)
except:
    action_file = codecs.open(InputFile,'r',encoding='iso8859-1')  #'iso8859-1')
    result, Genes = ParseActionFile(action_file)
action_file.close()

# First page
tableParaStyle = ParagraphStyle(name = 'Normal', leading = 9)
data = [
        ["PATIENT INFO","","SAMPLE","","REFERING PHYSICIAN",""],
        ["Name:",PatientName,"Date Collected:","","Name:",args.PhName],
        ["Age:",Age,"Date Received:",SampleDate.strftime('%m/%d/%Y'),"Institution:",Paragraph("<font size=7>%s</font>"%Institution,tableParaStyle)],
        ["Sex:",Sex,"Date of Report:",ReportDate.strftime('%m/%d/%Y'),"Address:",Paragraph("<font size=7>%s</font>"%PhysicianAddress,tableParaStyle)],
        ["Address:",Paragraph("<font size=7>%s</font>"%PatientAddress,tableParaStyle),"lab ID:",Accession+'\n',"",""],
        ["","","Source:",Source,"Contact:",""],
        ]

style1 = [
        ('SPAN',(0,0),(1,0)),
        ('SPAN',(2,0),(3,0)),
        ('SPAN',(4,0),(5,0)),
        ('SPAN',(-1,-3),(-1,-2)),  # order physician address merge
        ('SPAN',(-2,-3),(-2,-2)),  # order physician address merge
        #('SPAN',(1,-2),(1,-1)),    # patient address merge
        ('ALIGN',(0,0),(-1,0),"CENTRE"),
        ('ALIGN',(0,1),(0,-1),"RIGHT"),
        ('ALIGN',(1,1),(1,-1),"LEFT"),
        ('ALIGN',(2,1),(2,-1),"RIGHT"),
        ('ALIGN',(3,1),(3,-1),"LEFT"),
        ('ALIGN',(4,1),(4,-1),"RIGHT"),
        ('ALIGN',(5,1),(5,-1),"LEFT"),
        #('GRID', (0,0),(-1,-1),1, colors.blue),
        ('VALIGN',(0,0),(-1,-1),"TOP"),
        ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor("#0067b1")),
        ('FONT',(0,0),(-1,0),"Helvetica-Bold"),
        ('FONTSIZE', (0, 0), (-1, -1), 8), 
        ('LINEBELOW',(0,-1),(-1,-1),0.5, colors.HexColor("#0067b1")), 
         ]


Table_patient = header(data,style=style1,klass=Table, colWidths=[20*mm,35*mm,30*mm,35*mm,30*mm,35*mm], rowHeights=[5*mm,4*mm,4*mm,4*mm,4*mm,10*mm])


Logo = Image(scriptFolder+"./img/OncoGxOne_Plus_report.png",width = 75*mm, height = 14*mm)
myTitle1 = Paragraph("<font size=13><b>Tumor Profile for %s</b></font><br /><font size=9 color='#0067b1'><b>%s</b></font>"%(PatientName.decode('utf-8'),condition),style=ParagraphStyle("Caption", alignment=TA_LEFT))
#myTitle1 = Paragraph("<font size=13><b>Tumor Profile for %s</font><br /><font size=9>ICD-10: %s</b></font>"%(PatientName.decode('utf-8'),ICD_description),style=ParagraphStyle("Caption", alignment=TA_LEFT))
Table1 = header([[myTitle1,Logo]],style =[("ALIGN",(1,0),(1,0),"RIGHT"),("VALIGN",(0,0),(1,0),"TOP")], klass=Table, sep=0.2, colWidths=[107*mm,80*mm])
# Key findings

if len(result["Alteration_list"])==0:
    summary_word = "<font size=14 color='#0067b1'><b>NEGATIVE</b></font>"
    summary_content = "No Medically Actionable Mutations Detected."
else:
    summary_word = "<font size=14 color='red'><b>POSITIVE</b></font>"
    summary_content = "Mutations Detected: %s"%(", ".join(result["Alteration_list"]))

Summary = Paragraph("<font size=13>Result: </font>"+summary_word+"<br /><font size=10>%s</font>"%(summary_content),style=ParagraphStyle("Caption", alignment=TA_LEFT))


Key_finding_style = [
        ('LINEBELOW',(0,-1),(-1,-1),0.5, colors.black),
        ('TOPPADDING', (0,1), (-1,-2), 0),
        ('BOTTOMPADDING', (0,1), (-1,-2), 0),
]
ListStyle = ParagraphStyle(name = 'Normal', leftIndent=37, bulletIndent=20, fontSize=9, spaceBefore=-1)
List = ParagraphStyle(name = 'Normal', leftIndent=10, bulletIndent=0, spaceBefore=1, fontSize = 9, leading = 12)
n_Line=0 # record the Line number


ClinBenefitsSame_FirstPage=[]
ClinBenefitsDiff_FirstPage=[]
LackClinBenefits=[]
Key_finding_content=[[Paragraph("<font size=12><b>KEY FINDINGS</b></font>",ParaStyle)]]
for bene in result['ClinBenefitsSame']:
    if bene[0]=="Gene" or bene[0].startswith("No medically"): continue
    color = "#238943"
    n_Line+=1
    if [bene[2],bene[0]+"-"+bene[1]] not in ClinBenefitsSame_FirstPage:
        ClinBenefitsSame_FirstPage.append([bene[2],bene[0]+"-"+bene[1]])
    Line = "<font color='%s'><b>Potential Clinical Benefit </b></font> in %s with <font color='%s'><b>%s</b></font> due to <i>%s</i> %s.<br />"%(color,bene[3],color,bene[2],bene[0],bene[1])
    Key_finding_content.append([Paragraph(Line,ListStyle,bulletText="%d. "%n_Line)])
for bene in result['ClinBenefitsDiff']:
    if bene[0]=="Gene" or bene[0].startswith("No medically"): continue
    color = "#0067b1"
    n_Line+=1
    if [bene[2],bene[0]+"-"+bene[1]] not in ClinBenefitsDiff_FirstPage:
        ClinBenefitsDiff_FirstPage.append([bene[2],bene[0]+"-"+bene[1]])
    Line = "<font color='%s'><b>Potential Clinical Benefit </b></font> in %s with <font color='%s'><b>%s</b></font> due to <i>%s</i> %s.<br />"%(color,bene[3],color,bene[2],bene[0],bene[1])
    Key_finding_content.append([Paragraph(Line,ListStyle,bulletText="%d. "%n_Line)])
for Lackbene in result['LackClinBenefits']:
    if Lackbene[0]=="Gene" or Lackbene[0].startswith("No medically"): continue
    color = "#d89234"
    n_Line+=1
    if [Lackbene[2],Lackbene[0]+"-"+Lackbene[1]] not in LackClinBenefits:
        LackClinBenefits.append([Lackbene[2],Lackbene[0]+"-"+Lackbene[1]])
    Line = "<font color='%s'><b>Potential Drug Resistance </b></font> in %s with <font color='%s'><b>%s</b></font> due to <i>%s</i> %s.<br />"%(color,Lackbene[3],color,Lackbene[2],Lackbene[0],Lackbene[1])
    Key_finding_content.append([Paragraph(Line,ListStyle,bulletText="%d. "%n_Line)])
previous_side_effect_key = "" # make sure there is no duplicates on the key finding box for side effects
for SE in result['SideEffect']:
    if SE[0]=="Gene" or SE[0].startswith("No medically"): continue
    drugs = SE[2].split(": ")[0]
    if (SE[0]+drugs) != previous_side_effect_key:
        n_Line+=1
        Line = "Potential Clinical Side Effects with <b>%s</b> due to <i>%s</i> genotype.<br />"%(drugs,SE[0])
        Key_finding_content.append([Paragraph(Line,ListStyle,bulletText="%d. "%n_Line)])
        previous_side_effect_key = SE[0]+drugs
if n_Line==0:
    Key_finding_content.append([Paragraph("&nbsp&nbsp&nbsp&nbsp No medically actionable mutations detected.",ParaStyle)])
Key_finding_content.append([Paragraph("<font size=8><i>* The Key Findings section is an overview of potential therapeutic benefit or lack thereof. Please refer to the information below for details.</i></font>", ParaStyle)])
Key_finding = header(Key_finding_content, Key_finding_style, klass=Table, colWidths=[188*mm])

ClinTrial_FirstPage = [[x,str(len(result['ClinTrial'][x])-1)] for x in Genes]



def generateTable_firstpage(list1, list2):
    '''  combine two list table in the same horizontal level as one combined table '''
    combine_list = []
    for i in range(max(len(list1),len(list2))):
        try:
            temp1 = [Paragraph("<font size=8>%s</font>"%x, ParagraphStyle(name="centeredStyle", alignment=TA_CENTER)) for x in list1[i]]
        except:
            temp1 = ["",""]
        try:
            temp2 = [Paragraph("<font size=8>%s</font>"%x, ParagraphStyle(name="centeredStyle", alignment=TA_CENTER)) for x in list2[i]]
        except:
            temp2 = ["",""]
        combine_list.append(temp1+[""]+temp2)
    if len(combine_list)==0: combine_list=[["","","","",""]]
    Table_combine = header(combine_list, style=[("ALIGN",(0,0),(-1,-1),"CENTRE"),("VALIGN",(0,0),(-1,-1),"TOP")],klass=Table, sep=0.70, 
				colWidths=[35*mm,35*mm,24*mm,35*mm,35*mm], rowHeights=[(57.5/len(combine_list))*mm]*len(combine_list))
    return Table_combine

FirstPage_table1 = generateTable_firstpage(ClinBenefitsSame_FirstPage, ClinBenefitsDiff_FirstPage)
FirstPage_table2 = generateTable_firstpage(LackClinBenefits, ClinTrial_FirstPage)
pprint.pprint(ClinBenefitsSame_FirstPage)


### first three tables 
myTitle2 = Paragraph("<font size=9><b>Medically Actionable Alterations</b></font>",style=ParagraphStyle("Caption", alignment=TA_LEFT))
Title2 = header([[myTitle2]],style =[("ALIGN",(0,0),(0,0),"LEFT")], klass=Table, colWidths=[190*mm])
ClinBenefitSameTable = stripe_table(result['ClinBenefitsSame'], "Therapies With Potential Clinical Benefit - Same Tumor Type", '#238943', 'SameType_Sensi.png',sep=0.2)
ClinBenefitDiffTable = stripe_table(result['ClinBenefitsDiff'], "Therapies With Potential Clinical Benefit - Different Tumor Type", '#0067b1', 'DiffType_Sensi.png',sep=0.2)
LackClinBenefitTable = stripe_table(result['LackClinBenefits'], "Therapies With Potential Drug Resistance - Same Tumor Type", '#d89234', 'SameType_Resis.png',sep=0.2)
Page_one = [Table_patient, Table1, Spacer(0.1*inch, 0.1*inch), Summary, Spacer(0.1*inch, 0.3*inch), FirstPage_table1, Spacer(0.1*inch, 0.4*inch), FirstPage_table2, PageBreak(), Key_finding, Spacer(1.0*inch, 0.1*inch), Title2, ClinBenefitSameTable, ClinBenefitDiffTable, LackClinBenefitTable, Spacer(0.1*inch, 0.3*inch)]

for guideline in result['Guideline']:
    guideline_para = Paragraph("<b>%s:</b> %s"%(guideline[0],guideline[1]),List,bulletText="\xe2\x80\xa2")
    Page_one.append(guideline_para)
Elements.extend(Page_one)

# page 2 clinical trials
if len(Genes)!=0:
    myTitle4 = Paragraph("<font size=12><b>CLINICAL TRIALS TO CONSIDER</b></font>",style=ParagraphStyle("Caption", alignment=TA_LEFT))
    Title_CT = header([[myTitle4]],style =[("ALIGN",(0,0),(0,0),"LEFT")], klass=Table, colWidths=[190*mm])
    ClinTrials=[]
    for Gene in Genes:
        firstCT=False
        if Gene==Genes[0]:
            firstCT=True
        ClinTrialTable = stripe_table(result['ClinTrial'][Gene], "%d. %s Associated Clinical Trials"%(len(ClinTrials)+1,Gene), '#472c77', 'ClinTrial_icon.png', firstCT, sep=0.2)
        ClinTrials.append(ClinTrialTable)
    Page_two = [PageBreak()]+ClinTrials
    CT_annotation = Paragraph("<font size=9><i><br /># The two locations closest to the patient’s address based on zip code are shown (for US locations, otherwise show all locations).<br /><b>Note: Select clinical trials are shown. For a full list of clinical trials, please search the ClinicalTrials.gov website.</b></i></font>",style=ParagraphStyle("Normal", alignment=TA_LEFT))
    Page_two.extend([CT_annotation])
    Elements.extend(Page_two)


Page_three = [PageBreak()]
##alteration details tablesi
if len(result['MutDetail'])!=0:
    myTitle3 = Paragraph("<font size=12><b>%s</b></font>"%("Alteration Details with Therapeutic Implications by Tumor Type".upper()),style=ParagraphStyle("Caption", alignment=TA_LEFT))
    Title3 = header([[myTitle3]],style =[("ALIGN",(0,0),(0,0),"LEFT")], sep=0.3, klass=Table, colWidths=[190*mm])
    Page_three.append(Title3)
    mutDetail_table_style=[
             ('SPAN',(0,0),(-1,0)),
             ('BOX',(0,0),(-1,-1),1,colors.HexColor('#404040')),
             ('BACKGROUND',(0,0),(-1,2),colors.HexColor('#404040')),
             ('FONT',(0,0),(-1,-1),"Helvetica-Bold"),
             ('TEXTCOLOR',(0,1),(-1,2), colors.HexColor('#ffffff')),
             ('VALIGN',(0,3),(-1,-1),"TOP")
    ]

    for mutDetail in result["MutDetail"]:
        tmp_style=mutDetail_table_style
        for i in range(len(mutDetail)-2):
            tmp_style.append(('SPAN',(0,i+2),(1,i+2)))
        mutDetail_table = header(mutDetail,style=tmp_style,klass=Table,sep=0.2,colWidths=[30*mm,57*mm, 100*mm])
        Page_three.append(mutDetail_table)
    MutD_annotation = Paragraph("<font size=9><i><br /><b>Genes with medically actionable alterations are shown above. No alterations of known clinical significance were detected in the remainder of the OncoGxOne Plus Panel Genes shown in Table 1.</b></i></font>",style=ParagraphStyle("Normal", alignment=TA_LEFT))
    Page_three.extend([MutD_annotation, Spacer(5.0*inch, 0.2*inch)]) 

SideEffectTable = stripe_table(result['SideEffect'], "THERAPIES WITH POTENTIAL CLINICAL SIDE EFFECTS", '#ffffff', 'Side_Effect.png',sep=0.2)

Page_three.append(SideEffectTable)


TMB_included = True
TMB_content = """
Tumor mutation burden (TMB) is a measurement of the number of somatic mutation per mega base (MB) in coding regions of a tumor genome. TMB is a quantitative and genomic-based biomarker for cancer immunotherapy, and it has been proven to be more reliable than individual gene biomarkers, such as PD-L1 protein expressions. OncoGxOne\xe2\x84\xa2 Plus classifies tumor mutation burden into two different categories: TMB-High with mutations > 10 per MB, and TMB-Low with mutations <= 10 per MB. Tumors with higher levels of TMB are shown to express more neoantigens (a class of cancer-specific antigens) that may lead to more favorable immune response and higher efficacy using immune checkpoint inhibitors. Paired tumor and normal tissue are commonly used to assess TMB status using Whole Exome Sequencing (WES). Admera Health’s unique analysis enables highly accurate (95%) TMB prediction with tumor-only sample without matched normal.
"""
result['TMB_table'] = [["","Tumor Mutation Burden Result",""], ["",result['TMB'][0]+" (Probability: %s)"%result['TMB'][1], ""]]
if TMB_included:
    TMB_table = stripe_table(result['TMB_table'], "Tumor Mutation Burden (TMB) prediction results", "#ffffff", "TMB_icon.png", sep=0.2)
    TMB_annotation = Paragraph("<font size=9><br /><b>%s</b></font>"%TMB_content,style=ParagraphStyle("Normal", alignment=TA_LEFT))
    Page_three.extend([PageBreak(), TMB_table, TMB_annotation])

if len(result['HLAtyping'])!=0:
    result['HLAtyping'].insert(0,["Gene","Allele 1", "Allele 2"])
    HLATable = stripe_table(result['HLAtyping'], "Information of HLA genotyping Detected", "#ffffff", "HLA_icon.png", sep=0.2)
    HLA_annotation = Paragraph("<font size=9><i><br /><b>The HLA genes locate in chromosome 6 and are highly polymorphic, which means that they have many different alleles, allowing them to fine-tune the adaptive immune system. The human leukocyte antigen (HLA) system or complex is a gene complex encoding the major histocompatibility complex (MHC) proteins in humans. These cell-surface proteins are responsible for the regulation of the immune system in humans.</b></i></font>",style=ParagraphStyle("Normal", alignment=TA_LEFT))
if TMB_included:
    Page_three.extend([Spacer(15.0*inch, 0.2*inch), HLATable, HLA_annotation])
else:
    Page_three.extend([PageBreak(), HLATable, HLA_annotation])

Elements.extend(Page_three)




# Page Three About mutation information
if len(result['GeneInfo'])!=0:
    Key_finding_style = ParagraphStyle(name="normal")
    myTitle5 = Paragraph("<font size=12><b>%s</b></font>"%("About Genes".upper()),style=ParagraphStyle("Caption", alignment=TA_LEFT))
    Title5 = header([[myTitle5]],style =[("ALIGN",(0,0),(0,0),"LEFT")], klass=Table, colWidths=[190*mm])
    GeneInfo_string="<br />".join(["<font size=12 color='#0067b1'><b><i>%s</i></b></font><font size=10><br />%s<br /><br /><u>Mutation location in gene and/or protein</u><br />%s<br /><br /><u>Mutation prevalence</u><br />%s<br /><br /><u>Effect of mutation</u><br />%s<br /><br /></font>"%(GeneInfo['Gene'],GeneInfo['Comment'],GeneInfo['Mutation location in gene and/or protein'].replace("|","<br />"),GeneInfo['Mutation prevalence'].replace("|","<br />"),GeneInfo['Effect of mutation'].replace("|","<br />")) for GeneInfo in result['GeneInfo']])
    GeneInfo_box = Paragraph("<font size=11>%s</font>"%GeneInfo_string, Key_finding_style)
    Page_four = [PageBreak(), Title5, Spacer(5.0*inch, 0.2*inch),GeneInfo_box]
    Elements.extend(Page_four)


# page Four Cancer Drug information
if len(result['DrugInfo'])!=0:
    myTitle6 = Paragraph("<font size=12><b>%s</b></font>"%("Cancer Drug Information".upper()),style=ParagraphStyle("Caption", alignment=TA_LEFT))
    Title6 = header([[myTitle6]],style =[("ALIGN",(0,0),(0,0),"LEFT")], klass=Table, colWidths=[190*mm])
    Title6.keepWithNext=True
    Page_four = [PageBreak(), Title6,Spacer(5.0*inch, 0.2*inch)]
    for drug in result['DrugInfo']:
        Page_four.append(Paragraph("<font size=11><b>%s</b><br /><link href='%s' color='#1111ee'><u>%s</u></link><br /><br /></font>"%(drug[0],drug[1],drug[1]), ParaStyle))
    Page_four.append(PageBreak())
    Elements.extend(Page_four)



#  Information Page
myTitle7 = Paragraph("<font size=11><b>Table 1: OncoGxOne\xe2\x84\xa2 Plus Panel Genes</b></font>",style=ParagraphStyle("Caption", alignment=TA_LEFT))
Title7 = header([[myTitle7]],style =[("ALIGN",(0,0),(0,0),"LEFT")], klass=Table, colWidths=[190*mm])
Info_para = Paragraph("<font size=10>OncoGxOne\xe2\x84\xa2 Plus is a single-panel cancer test panel designed to provide comprehensive genomic analysis for cancer therapy. This test detects all types of genetic alterations (point mutations, small insertions/deletions, gene fusions, copy number variations) in the 333 genes listed in the table below. Gene coverage includes all coding exons and untranslated regions (UTRs), as well as select intronic region known to be involved in gene fusion events.</font>",ParaStyle)

Info_file = open(scriptFolder+"OncoGxOnePlus_gene_list.txt",'r')
Data_info = [x.split("\t") for x in Info_file.read().strip().split("\n")]
tableStyle1 = [
        ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor("#ffc000")),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#404040")),
        ('GRID',(0,1),(-1,-1),0.5,colors.black),
        ('FONT',(0,1),(-1,0),"Helvetica-Bold"),
        ('SPAN',(0,0),(-1,0)),
        ('ALIGN',(0,0),(-1,-1),"CENTRE")
    ]
tableStyle2 = [
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('ALIGN',(0,0),(-1,-1),"CENTRE")
    ]   

Table_info1 = header(Data_info[:32],style =tableStyle1, klass=Table, sep=0.2, colWidths=[22*mm]*8, rowHeights=[6*mm]*32)
Table_info2 = header(Data_info[32:],style =tableStyle2, klass=Table, sep=0.2, colWidths=[22*mm]*8, rowHeights=[6*mm]*11)
Page_info = [Title7, Spacer(5.0*inch, 0.2*inch), Info_para, Table_info1, PageBreak(), Table_info2, PageBreak()]
Elements.extend(Page_info)



## Last page
myTitle8 = Paragraph("<font size=11><b><u>References:</u></b></font>",style=ParagraphStyle("Caption", alignment=TA_LEFT))
Title8 = header([[myTitle8]],style =[("ALIGN",(0,0),(0,0),"LEFT")], klass=Table, colWidths=[193*mm])
Page_last = [Title8,]
Color = '#1111ee'  # link color
Page_last.extend([
      Paragraph("NCCN Biomarkers Compendium at: <font color='%s'><u>http://www.nccn.org/professionals/biomarkers/content/</u></font>"%Color, List, bulletText="\xe2\x80\xa2"),
      Paragraph("U.S. Food and Drug Administration, Table of Pharmacogenomic Biomarkers in Drug Labeling. Available online at: <br /><font color='%s'><u>http://www.fda.gov/Drugs/ScienceResearch/ResearchAreas/Pharmacogenetics/ucm083378.htm</u></font>"%Color, List, bulletText="\xe2\x80\xa2"),
      Paragraph("My Cancer Genome at: <font color='%s'><u>http://www.mycancergenome.org/</u></font>"%Color, List, bulletText="\xe2\x80\xa2"),
      Paragraph("PharmGKB: The Pharmacogenomics Knowledgebase. Available online at: <font color='%s'><u>http://www.pharmgkb.org/index.jsp</u></font>"%Color, List, bulletText="\xe2\x80\xa2"),
      Paragraph("The Clinical Pharmacogenetics Implementation Consortium (CPIC) Guideline. Available online at: <br /><font color='%s'><u>https://www.pharmgkb.org/page/cpic</u></font>"%Color, List, bulletText="\xe2\x80\xa2"), 
      Paragraph("European Medicines Agency, Multidisciplinary: Pharmacogenomics. Available online at: <br /><link href='http://www.ema.europa.eu/ema/index.jsp?curl=pages/regulation/general/general_content_000411.jsp&mid=WC0b01ac058002958e' color='%s'><u>http://www.ema.europa.eu/ema/index.jsp?curl=pages/regulation/general/general_content_000411.jsp&mid=WC0b01ac058002958e</u></link>"%Color, List, bulletText="\xe2\x80\xa2"),
      Paragraph("Swen JJ et al. Pharmacogenetics: from bench to byte - an update of guidelines. Clin Pharmacol Ther. 89(5):662-73.", List, bulletText="\xe2\x80\xa2"),
      Paragraph("Catalogue Of Somatic Mutations In Cancer (COSMIC) at: <font color='%s'><u>cancer.sanger.ac.uk</u></font>"%Color, List, bulletText="\xe2\x80\xa2"),
])
for ref in result["Reference"]:
    Page_last.append(Paragraph(ref, List, bulletText="\xe2\x80\xa2"))

if len(result["Reference"])>2:   # if reference list is long, break the page after the last reference.
    Page_last.append(PageBreak())

content1 = '''
Target regions of interest were captured using a custom probe library and sequenced by massive parallel sequencing method (Illumina platform). The detected mutations are annotated based on hg19 reference genome assembly. The OncoGxOne\xe2\x84\xa2 Plus test was developed by Admera Health, including determination and validation of performance characteristics. The sensitivity and specificity of this test is greater than 98% and 97%, respectively, when a minimum of 10% tumor tissue is present in the sample. This test has not been approved by the U.S. Food and Drug Administration (FDA) and is for research purposes only. The Admera Health clinical laboratory is certified under the Clinical Laboratory Improvement Amendments of 1988 (CLIA), accredited by the College of American Pathologists, and is qualified to perform high complexity clinical laboratory testing.
'''

if len(result["Reference"])>5: # N-of-One's interpretation, add a acknowledgement
        content1 += "<br /><br /> N-of-One, Inc. has provided to Admera Health research, analysis and interpretation, on a patient specific basis, of peer- reviewed studies and publicly available databases.  This information may include the association between a specific molecular alteration and clinical benefit, or lack thereof, from FDA-approved therapies and therapies under clinical investigation. Additional information from N-of-One is available on its website at www.n-of-one.com."


content2 = '''
The information contained in this report is provided as a service and does not constitute medical advice. At the time of report generation this information is believed to be current and is based upon published research; however, research data evolves and amendments to the prescribing information of the drugs listed will change over time. While this report is believed to be accurate and complete as of the date issued, THE DATA IS PROVIDED "AS IS", WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. As medical advice must be tailored to the specific circumstances of each case, the treating health care professional has ultimate responsibility for all treatment decisions made with regard to a patient including any made on the basis of a patient's genotype.
'''


Page_last.extend([
      Spacer(0.2*inch, 0.2*inch),
      Paragraph("<font size=9 color='#3350bd'><i><b>Test Methodology and Limitations for OncoGxOne\xe2\x84\xa2 Plus: </b><br />%s<br /><br /><b>Disclaimer of Liability:</b><br />%s</i></font>"%(content1,content2),style=ParagraphStyle("Caption", alignment=TA_JUSTIFY)),
      Spacer(0.2*inch, 0.2*inch),
      Paragraph("<font size=11><b>I certify that these lab results are accurate.</b></font>", styles['Normal']),
      Spacer(0.2*inch, 0.1*inch),
      Paragraph("<font size=13>Signatures: </font>", styles['Normal']),
      Spacer(0.2*inch, 0.6*inch),
      Paragraph("<font size=11>James J. Dermody, Ph.D.<br />Laboratory Director<br />Admera Health LLC<br /></font>", style=ParagraphStyle("Normal",leading=12)),
      Spacer(0.2*inch, 0.3*inch),
      Paragraph("<font size=10>Testing and interpretation performed by: Admera Health LLC, 126 Corporate Blvd, South Plainfield, NJ 07080<br />Tel.# +1-908-222-0533. James Dermody Ph.D. Laboratory Director<br /><br />OncoGxOne\xe2\x84\xa2 Plus is a trademark of Admera Health, LLC.</font>", style=ParagraphStyle("Normal",leading=12))
      ])

Elements.extend(Page_last)
go()
