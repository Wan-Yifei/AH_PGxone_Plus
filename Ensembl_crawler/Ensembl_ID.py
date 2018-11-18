# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 16:17:31 2018

@author: wan_yifei
"""

import sys
import urllib
import urllib.request as urllib2
import json
import time
import argparse

# 1. Accept arguments from cmd
def ParseArg():

    p = argparse.ArgumentParser(description="Query Ensembl ID by gene name")
    p.add_argument("Species",type=str, help="Indicate the species")
    p.add_argument("Genes",type=str, help="The path of gene list")
    p.add_argument("Output",type=str,help="output file name")
    if len(sys.argv)==1:
        print >>sys.stderr,p.print_help()
        sys.exit(0)
    return p.parse_args()

# 2. Define client for ensembl

class EnsemblRestClient(object):
    
    ## 2.1 Initial class
    def __init__(self, server='http://rest.ensembl.org', reqs_per_sec=15):
        self.server = server
        self.reqs_per_sec = reqs_per_sec
        self.req_count = 0
        self.last_req = 0

    ## 2.2 Connect method
    def perform_rest_action(self, endpoint, hdrs=None, params=None):
        if hdrs is None:
            hdrs = {}

        if 'Content-Type' not in hdrs:
            hdrs['Content-Type'] = 'application/json'

        if params:
            endpoint += '?' + urllib.parse.urlencode(params)
            #print(endpoint)

        data = None

        ## check if we need to rate limit ourselves or IP will be banned
        if self.req_count >= self.reqs_per_sec:
            delta = time.time() - self.last_req
            if delta < 1:
                time.sleep(1 - delta)
            self.last_req = time.time()
            self.req_count = 0
        
        try:
            request = urllib2.Request(self.server + endpoint, headers=hdrs) ## connect to server and request info
            #print(request)
            response = urllib2.urlopen(request) ## open the response from server
            #print(type(response))
            content = response.read()
            if content:
                data = json.loads(content)
            self.req_count += 1

        except urllib2.HTTPError as e:
            # check if we are being rate limited by the server
            if e.code == 429:
                if 'Retry-After' in e.headers:
                    retry = e.headers['Retry-After']
                    time.sleep(float(retry))
                    self.perform_rest_action(endpoint, hdrs, params)
            else:
                sys.stderr.write('Request failed for {0}: Status code: {1.code} Reason: {1.reason}\n'.format(endpoint, e))
           
        return data
    
    ## 2.3 Query method
    def get_genes(self, species, name): ## name: the name of gene
        genes = self.perform_rest_action(
            '/xrefs/symbol/{0}/{1}'.format(species, name), 
            params={'object_type': 'gene'} ## query gene ID
        )
        return genes

# 3. Main function

def run(species, name):
    client = EnsemblRestClient()
    gene = client.get_genes(species, name)
    if gene:
        #print(gene['id'])
        return(gene[0])
    else:
        gene = {'id' : 'Not found'}
        #print(gene)
        return(gene)
            
# 4. Run script        
            
if __name__ == '__main__':
    args = ParseArg()
    species = args.Species
    genes = args.Genes
    output = open(args.Output, mode='a+', encoding='utf-8')
    print("{}\t{}".format('Gene', 'Ensembl_ID'), file = output)
    with open(genes) as gene_name:
        gene_names = gene_name.readlines()
        for name in gene_names:
            gene = run(species, name.strip())
            print("{}\t{}".format(name.strip(), gene['id']))
            print("{}\t{}".format(name.strip(), gene['id']), file = output)
        output.close()    
            