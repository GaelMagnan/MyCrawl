from HtmlParse import toSite

AllPages={}
AllSites={}

class Page:
	corpus=[]
	sizeTop=0
	def __init__(self, myURL):
		self.Peres=[]
		self.Fils=[]
		self.FilsUrl=[]
		self.words={}
		self.relevanceCorpus={}
		self.deadEnd=False
		self.errorDL=False
		self.errorRead=False
		self.notRelevent=False
		self.relevantByCorpus=False
		self.handled=False
		self.URL=myURL
		siteURL=toSite(myURL)
		if siteURL not in AllSites:
			AllSites[siteURL]=Site(siteURL)
		AllSites[siteURL].addPage(self)
		self.Site=AllSites[siteURL]
		AllPages[myURL]=self
	
	def addPere(self, pere):
		self.Peres.append(pere)
	
	def addFils(self, filsURL):
		if filsURL not in AllPages:
			AllPages[filsURL]=Page(filsURL)
		self.Fils.append(AllPages[filsURL])
		AllPages[filsURL].addPere(self)

	def setWords(self,words):
		self.words=words
		for w in Page.corpus:
			if w in self.words:
				self.relevanceCorpus[w]=self.words[w]
			else:
				self.relevanceCorpus[w]=0
	
	def checkCorpusRelevance(self):
		if len(Page.corpus)==0 :
			return True
		for count in self.relevanceCorpus:
			if count>0:
				return True
		return False
	
	def checkRelevance(self,page, degree, degreeTotal):
		top=page.getTopWords()
		total=0
		for tab in top:
			w=tab[1]
			if w in self.words:
				if self.words[w]>degree:
					return True
				elif self.words[w]>0:
					total+=self.words[w]
					if total>degreeTotal:
						return True
		return False
	
	def checkAllRelevance(self, degree, degreeTotal):
		for pe in self.Peres:
			if self.checkRelevance(pe,degree,degreeTotal):
				return True
		return False
	
	def clean(self):
		for fi in self.Fils:
			if not fi.handled:
				return
		self.words={}

	def cleanFathers(self):
		for pe in self.Peres:
			pe.clean()

	def getTopWords(self):
		top=[]
		for word, count in self.words.iteritems():
			if top ==[]:
				top.append([count,word])
			elif top[0][0]>count and len(top)<Page.sizeTop:
				continue
			elif top[0][0]<=count and len(top)<Page.sizeTop:
				top.insert(0,[count,word])
			else:
				top.pop(0)
				i=0
				for a in top:
					if a[0]<count:	
						i=i+1
						continue
					else:
						top.insert(i,[count,word])
						break
				if i==len(top):
					top.append([count,word])
		return top

class Site:

	def __init__(self, myURL):
		self.URL=myURL
		self.Pages=[]
	
	def addPage(self, page):
		self.Pages.append(page)

	def isRelevant(self):
		for p in self.Pages:
			if not p.deadEnd:
				return True
		return False
