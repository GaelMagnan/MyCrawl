import networkx as nx
import os
from Data import Page
from Data import Site
from Data import AllPages
from Data import AllSites

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.mkdir(d)

def addNodePage(G,page):
	attr={}
	if page.relevantByCorpus:
		attr['relevant']='ByCorpus'
	else:
		attr['relevant']='ByRelation'
	for word,count in page.relevanceCorpus.iteritems():
		attr[word]=str(count)
	i=Page.sizeTop
	for tmp in page.getTopWords():
		attr['Top'+str(i)+"word"]=tmp[1]
		attr['Top'+str(i)+"value"]=tmp[0]
		i=i-1
	G.add_node(page.URL,attr)
	
def addNodeSite(G,site):
	G.add_node(site.URL)

def addEdgePage(G,source,dest):
	G.add_edge(source.URL,dest.URL)

def addEdgeSite(G,source,dest):
	G.add_edge(source.URL,dest.URL)

def createGraphPage():
	G=nx.DiGraph()
	for url,page in AllPages.iteritems():
		if not page.deadEnd:
			addNodePage(G,page)
	for url,page in AllPages.iteritems():
		if not page.deadEnd:
			for b in page.Fils:
				addEdgePage(G,page,b)
	return G

def createGraphSite():
	G=nx.DiGraph()
	for url,site in AllSites.iteritems():
		if site.isRelevant():
			addNodeSite(G,site)
	for url,site in AllSites.iteritems():
		if site.isRelevant():
			for b in site.Pages:
				if not b.deadEnd:
					for c in b.Fils:
						addEdgeSite(G,site,c.Site)
	return G

def saveGraphs(outputFile):
	nx.write_gexf(createGraphPage(),"page"+outputFile)
	nx.write_gexf(createGraphSite(),"site"+outputFile)

def timedSave(outputFile,nbrSave):
	ensure_dir("./Saved/page"+str(nbrSave)+outputFile)
	nx.write_gexf(createGraphPage(),"./Saved/page"+str(nbrSave)+outputFile)
	nx.write_gexf(createGraphSite(),"./Saved/site"+str(nbrSave)+outputFile)
	

