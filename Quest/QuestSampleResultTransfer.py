import os, sys, argparse, datetime
from PWNAPI import *
import xml.etree.ElementTree as ET
import pySyncplicity
scriptFolder = os.path.dirname(os.path.abspath(sys.argv[0]))+"/"
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ParseArg():
    p=argparse.ArgumentParser(
            description="QuestSampleResultTransfer: Daily transfer of PGxOne Plus report, result and patietn information files to PWN or Quest",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('-R', '--reportFolder', type=str, help='Folder of PDF report', default='/reportdata/')
    p.add_argument('-p', '--masterPHIfile', type=str, help='Path of master PHI file', default='/reportdata/Quest_PHI/master_PHI_info.txt')
    subparsers = p.add_subparsers(help="All available sub commands") ## yifei: Sub-command
    parser_run = subparsers.add_parser('run', help='run one daily iteration of QuestSampleResultTransfer')
    parser_run.set_defaults(func=run)
    parser_sendPWN = subparsers.add_parser('sendPWN', help='send PDF of one sample to PWN')
    parser_sendPWN.add_argument("pdf", type=str, help='path of PDF file to be sent to PWN')
    parser_sendPWN.add_argument("pwnReq", type=str, help='PWN reqisition ID for this sample, 6-digit number')
    parser_sendPWN.add_argument("-n", "--normal", dest='abnormal', help="set the sample as normal when sending to PWN", action='store_false')
    parser_sendPWN.set_defaults(abnormal=True)
    parser_sendPWN.set_defaults(func=sendPWN)
    if len(sys.argv)==1:
        print >>sys.stderr,p.print_help()
        exit(0)
    return p.parse_args()

WarningMessage = []



def SendPDF_PWN(PDF_path, PWN_req, abnormal=True):
	## yifei: how to update record.txt? Answer: Line#64
    command = 'grep %s %s/Quest_PWN_API_response_record.txt'%(PWN_req, scriptFolder)
    run = os.popen(command)
    info_line = run.read().strip().split("\n")[0]
    run.close()
    if info_line!="":
        print >>sys.stdout, "Sample A-%s already sent to PWN previously, no need to send now"%PWN_req
        return True
    lab_key = "Pe5yEpUGCqU2nYF3JpWIZjIYrWsLoAay"
    lab_token = "VLGACTZJuv6kqOyfUNz2CZ5xlagY0ZTP"
    L = PWNAPI(lab_key, lab_token, env="production")
    currdate = str(datetime.datetime.now().date())
    pwn_value = 10
	## yifei: Send normal
    if not abnormal:
        pwn_value = 4
    data = "<hl7message><data><result><code>%s</code><order_code>30243</order_code><result_code>300</result_code><result_name>PGxOne Plus, 50 Gene Panel</result_name><analyte_name>PGxOne Plus</analyte_name><units>cc</units><value>%d</value><reference_range>2-5</reference_range> <lab_facility>XY^Admera Health^126 Corporate Blvd^South Plainfield^NJ^07080^Dr. James Dermody</lab_facility><date>%s</date></result></data></hl7message>"%(PWN_req, pwn_value, currdate)
    response = L.CreateResults(PWN_req, data, PDF_path) ## yifei: Send the PDF and the response should be xml.
    print response
	## yifei: Prepare warning messages:
    root = ET.fromstring(response)
    if root.tag == 'errors':
        error = root.find('error').text
        WarningMessage.append("Error in sending PDF to PWN for sample A-%s: %s"%(PWN_req, error))
        return False
    if root.tag == 'html':
        WarningMessage.append("Error in sending PDF to PWN for sample A-%s: %s"%(PWN_req, "502 Bad Gateway"))
        return False
    status = root.find('status').text
	## yifei: update record.txt
    if status in ['pending', 'approved']:
        line = "A-%s\t"%PWN_req+"\t".join([ele.text for ele in root])
        os.system('echo "%s" >> %s/Quest_PWN_API_response_record.txt'%(line, scriptFolder))
        return True

def FindActionFile(reqID):
	## yifei: the 18* should be updated manually!!
	## yifei: -mtime is a modification time  filter. It's in days.
    command = 'find /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/18*/Plus -mtime 0 | grep "LIS.txt" | grep "%s"'%(reqID) ## yifei: find corresponding LIS files
    run = os.popen(command)
    actionFile = run.read().strip().split("\n")[0]
    run.close()
	## yifei: if cannot find LIS for specified reqID:
    if actionFile.strip()=="":
        WarningMessage.append("Action file not found for sample '%s'"%(reqID))
        return None
	
	## yfiei: Add extra line at the top of LIS (Sop: #1.2).
	## yifei: Output file to tmp folder
    command = 'sed "1 i\##RequisitionNumber: %s" %s> /tmp/%s'%(reqID, actionFile, actionFile.split("/")[-1]) ## yifei: 'actionFile.split("/")[-1]' is the name of the LIS file.
    os.system(command)
    print >>sys.stdout, "Generated action file for sample %s in /tmp/"%(reqID)
    return "/tmp/%s"%actionFile.split("/")[-1]

def getPatientInfoFile(reqID, masterPHIfile):
	## yifei: How to update master PHI?
    command = 'grep %s %s'%(reqID, masterPHIfile)
    run = os.popen(command)
    info_line = run.read().strip().split("\n")[0]
    run.close()
    if info_line.strip()=="":
        WarningMessage.append("PatientInfo not found for sample '%s' in master PHI file %s"%(reqID, masterPHIfile))
        return None
	## yifei: Output a PHI_file in tmp folder
    PHI_file = "/tmp/%s_patientInfo.txt"%reqID
    os.system("head -n 1 %s > %s"%(masterPHIfile, PHI_file))
    os.system('echo "%s" >> %s'%(info_line, PHI_file))
    return PHI_file


def SendFlatFile(File_path):
    client = pySyncplicity.SyncplicityClient(username='pengfei.yu@admerahealth.com', password='AdmeraQuest123',verify=False)
    client.connect()
	## yifei: list_sync_points??
    syncpoints = client.list_sync_points()
    assert syncpoints[0].Name == 'PGx'
    response = client.upload_file(File_path, syncpoints[0].Id)
    return response

def outputWarning(WarningFileName):
    if len(WarningMessage)==0:
        return ## yifei: No error -> close function
    WarningFile = open(scriptFolder+WarningFileName, 'w')
    for c, w in enumerate(WarningMessage):
        print>>WarningFile, "Warning-%d: %s"%(c+1, w)
        print>>sys.stderr, "Warning-%d: %s"%(c+1, w)
    WarningFile.close()

def run(args):
    command = 'find %s/ -mtime 0 | grep "PGQD" | grep "pdf"'%args.reportFolder
    run = os.popen(command)
    daily_reports = [x.split("/")[-1] for x in run.read().strip().split("\n")]
    run.close()
    WarningFileName = "Warning"+datetime.datetime.now().strftime('-%m%d%Y%H%M')+".txt"
    for report in daily_reports:
        if report.strip()=="": continue
        PWN_req = report.split("_")[0].split("A-")[-1]
        SentPWN = SendPDF_PWN(args.reportFolder+"/"+report, PWN_req) ## yifei: line#34. Send PDF file.
        if SentPWN:
            print >>sys.stdout, "Report sent to PWN for sample A-"+PWN_req
        else:
            print >>sys.stdout, "Report FAILED to send to PWN for sample A-"+PWN_req
            print >>sys.stdout, "!!Please check the warning information file: %s"%(WarningFileName)
        ActionFile = FindActionFile("A-"+PWN_req) ## yifei: line#70, pathway of action file
        if ActionFile != None:
            response = SendFlatFile(ActionFile) ## yifei: line#105. Send action file.
            if not response.ok: ## yifei: line#111
                WarningMessage.append("ActionFile [%s] FAILED to be uploaded to Syncplicity: %s"%(ActionFile, response.content))
        PatientInfoFile = getPatientInfoFile("A-"+PWN_req, args.masterPHIfile)
        if PatientInfoFile != None:
            response = SendFlatFile(PatientInfoFile) ## yifei: Send patient lnfomation file
            if not response.ok:
                WarningMessage.append("PatientInfoFile [%s] FAILED to be uploaded to Syncplicity: %s"%(PatientInfoFile, response.content))
    outputWarning(WarningFileName)
    return 0

def sendPWN(args):
    pdf = args.pdf
    PWN_req = args.pwnReq
    abnormal = args.abnormal
    print >>sys.stdout, "PWN Req.: ", PWN_req
    print >>sys.stdout, "Abnormal: ", abnormal
    if not os.path.isfile(pdf):
        print >>sys.stderr, "Cannot find PDF file '%s'. Please specify the correct path of PDF file."%(pdf)
        sys.exit(0)
    print >>sys.stdout, "Result PDF: ", pdf
    WarningFileName = "Warning"+datetime.datetime.now().strftime('-%m%d%Y%H%M')+".txt"
    SentPWN = SendPDF_PWN(pdf, PWN_req, abnormal)
    if SentPWN:
        print >>sys.stdout, "Report sent to PWN for sample A-"+PWN_req
    else:
        print >>sys.stdout, "Report FAILED to send to PWN for sample A-"+PWN_req
        print >>sys.stdout, "!!Please check the warning information file: %s"%(WarningFileName)
    outputWarning(WarningFileName)
    return 0

args = ParseArg()
args.func(args)
