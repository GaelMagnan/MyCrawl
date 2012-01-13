import re
import BeautifulSoup
import htmlentitydefs
import string
	
stopWords={}

def unescape(text):
	def fixup(m):
		text = m.group(0)
		if text[:2] == "&#":
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				print "Value Error"
				pass
		else:
			try:
				if text[1:-1] == "amp":
					text = "&amp;amp;"
				elif text[1:-1] == "gt":
					text = "&amp;gt;"
				elif text[1:-1] == "lt":
					text = "&amp;lt;"
				#else:
				#	print text[1:-1]
				text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
			except KeyError:
				pass
		return text # leave as is
	return re.sub("&#?\w+;", fixup, text)



def getPreparedHtml(html):
	return BeautifulSoup.BeautifulSoup(html)

def extractlinks(soup):
    anchors = soup.findAll('a')
    links = []
    for a in anchors:
	try:
		tmp=a['href']
		if not tmp.startswith('http://') and not tmp.startswith('https://'):
			if not tmp.startswith('/') and not tmp.startswith('mailto:') and not tmp.startswith('#') and not tmp.startswith("javascript:") and not tmp=="" and not tmp.startswith(" "):
				tmp='http://'+tmp
			else:
				continue
	       	links.append(tmp)
	except KeyError,e:
		continue
    return links

def toSite(s):
	p = re.compile(r'^(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~\/|\/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))',re.I)
	m=p.match(s)
	if m!=None:
		return m.group(0)

def getLang(soup):
	html=soup.findAll(lang =True)
	if len(html)>0:
		if html[0] is not None:
			return html[0]['lang']
	return 'en'

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True


def getText(soup):
	if soup.head is not None:
		if soup.head.title is not None:
			title=soup.head.title.string
		else:
			title=""
	else:
		title=""
	#desc=soup.find("meta",name="description")
	#key=soup.find("meta",name="keywords")
	texts = soup.findAll(text=True)
	visible_texts = filter(visible, texts)
	output=unescape(title).strip()
	for t in visible_texts:
		output=output+" "+unescape(t).strip()
	return output
	
def getStopwords(lang):
	if lang in stopWords:
		return stopWords[lang]
	else:
		return {}

def getMatriceWords(soup):
	text=getText(soup)  
	ignorechars = ''',:'!.?'''
	wdict={}
	if text is None:
		return wdict
	words = text.split();
	stopwords=getStopwords(getLang(soup))
	reg=re.compile("[a-z]+['[a-z]+]?")
	for w in words:
		w = w.lower().strip(ignorechars)
		if not reg.match(w):
			continue
		if w.isdigit():
			continue
		if w in stopwords:
			continue
		elif w in wdict:
			wdict[w]+=1
		else:
			wdict[w] = 0
	return wdict

	
