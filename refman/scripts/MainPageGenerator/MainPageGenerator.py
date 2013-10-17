import json, urllib2, os
from BeautifulSoup import *

class MainPageGenerator:
    def __init__(self, path = "", test = False):
        self.path = path
        
        self.managersURL        = 'http://mantydze.web.cern.ch/mantydze/tcproxy.php?type=managers'
        self.usersURL           = 'http://mantydze.web.cern.ch/mantydze/tcproxy.php?type=users'
        self.CMSSWURL           = 'http://mantydze.web.cern.ch/mantydze/tcproxy.php?type=packages&release=CMSSW_4_4_2'
        
        self.tWikiLinks         = {'Analysis':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideCrab',
                                   'Calibration and Alignment':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideCalAli',
                                   'Core':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideFrameWork',
                                   'DAQ':'https://twiki.cern.ch/twiki/bin/view/CMS/TriDASWikiHome',
                                   'DQM':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideDQM',
                                   'Database':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideCondDB',
                                   'Documentation':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuide',
                                   'Fast Simulation':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideFastSimulation',
                                   'Full Simulation':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideSimulation',
                                   'Generators':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideEventGeneration',
                                   'Geometry':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideDetectorDescription',
                                   'HLT':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideHighLevelTrigger',
                                   'L1':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideL1Trigger',
                                   'Reconstruction':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideReco',
                                   'Visualization':'https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideVisualization'}
        
        self.data               = None
        
        self.GitLink            = "https://github.com/cms-sw/cmssw/tree/CMSSW_7_0_0_pre0/%s/%s"
        
        title = "<center>\n<h1>CMSSW Documentation</h1>\n<h2>CMSSW_7_0_0_pre4</h2>\n</center>\n"
        links = """
<p style="margin-left:10px;">
Learn <a href="ReferenceManual.html">how to build Reference Manual</a><br>
Learn more about <a target="_blank" href="http://www.stack.nl/~dimitri/doxygen/commands.html">special doxygen commands</a>
</p>\n\n"""
        head = """
<!-- Content Script & Style -->
<script type="text/javascript" src="jquery.js"></script>
<script type="text/javascript">
var itemList = [];

function toggleHoba(item, path)
{
    for(var i = 0; i < itemList.length; i++)
    {
        if(itemList[i] == item)
        {
            var iframe = $("#"+itemList[i]+"_div").children("iframe:first");
            if(!iframe.attr("src"))
            {
                iframe.attr("src", path)
            }
            $("#"+item+"_div").slideToggle();
        }
        else
            $("#"+itemList[i]+"_div").slideUp();
    }
}

$(document).ready(function() {
searchBox.OnSelectItem(0);
$(".doctable").find("td").each(function(){ if (this.id.indexOf("hoba_") != -1)itemList.push(this.id);});
});
</script>
<style>
.DCRow
{
    background: #eeeeff;
    border-spacing: 0px;
    padding: 0px;
    border-bottom: 1px solid #c1c1dc;
}

.DCRow:hover
{
    background: #cde4ec;
}
</style>
<!-- Content Script & Style -->
        """
        self.contentStamp       = '$CONTENT$'
        self.mainPageTemplate   = self.ReadFile("index.html")
        self.WriteFile("index_backup.html", self.mainPageTemplate)          #backup file
        soup     = BeautifulSoup(self.mainPageTemplate)
        soup.head.insert(len(soup.head), head)
        
        contents = soup.find("div", { "class" : "contents" })
        for child in contents.findChildren():
            child.extract()
        contents.insert(0, title + self.contentStamp + links)
        self.mainPageTemplate = str(soup)
        self.mainPageTemplate = self.mainPageTemplate.replace("CSCDQM Framework Guide", "")
        self.mainPageTemplate = self.mainPageTemplate.replace('&lt;','<').replace('&gt;', '>')
        print "Main page template created..."
        
        self.treePageTamplate   = self.ReadFile("tree_template.html", test) #!! pathFlag = False
        self.classesSource      = self.ReadFile("classes.html")
        self.filesSource        = self.ReadFile("files.html")
        self.packageSource      = self.ReadFile("pages.html")
        
    def ReadFile(self, fileName, pathFlag = True):
        """This method reads file directly or from path."""
        if pathFlag:
            print "Read:", self.path + fileName
            f = open(self.path + fileName)
        else:
            f = open(os.path.split(__file__)[0] + '/' + fileName)
            print "Read:", fileName
        data = f.read()
        f.close()
        return data
    
    def WriteFile(self, fileName, data):
        """This method writes data"""
        print "Write:", self.path + fileName
        f = open(self.path + fileName, "w")
        f.write(data)
        f.close()
        
    def GetFileName(self, fileName):
        """This method returns file name without extension"""
        if '.' in fileName:
            return fileName[0:fileName.find('.')]
        else:
            return fileName
    
    def ParseJsonFromURL(self, URL):
        """This method returns data which is read from URL"""
        u = urllib2.urlopen(URL)
        return json.loads(u.read())
    
    def __ParseItem(self, str_):
        return str_[0:str_.find('/')]
    
    def __ParseSubItem(self, str_):
        if '/' in str_:
            return str_[str_.find('/')+1:]
        else:
            return None
        
    def __GetHTMLItemDepth(self, item):
        return item["id"].count("_") - 2
    
    def __HTMLFileName(self, fileName):
        return fileName.lower().replace(' ', '_')
    
    def PrepareData(self):
        self.managers = self.ParseJsonFromURL(self.managersURL)
        print "Managers loaded and parsed..."
            
        self.users = self.ParseJsonFromURL(self.usersURL)
        print "Users loaded and parsed..."
        
        self.data = {}
        for i in self.managers.keys():
            self.data[i] = {"__DATA__":{"Contact":[]}}
            for j in self.managers[i]:
                self.data[i]["__DATA__"]["Contact"].append(self.users[j])
        self.domains = self.ParseJsonFromURL(self.CMSSWURL)
        print "Domains loaded and parsed..."
        
        for i in self.domains.keys():
            for j in self.domains[i]:
                if not self.data[i].has_key(self.__ParseItem(j)):
                    self.data[i][self.__ParseItem(j)] = {}
                if not self.data[i][self.__ParseItem(j)].has_key(self.__ParseSubItem(j)):
                    self.data[i][self.__ParseItem(j)][self.__ParseSubItem(j)] = {}
                
                self.data[i][self.__ParseItem(j)][self.__ParseSubItem(j)]["__DATA__"] = {
                    'git': self.GitLink % (self.__ParseItem(j), self.__ParseSubItem(j))
                    }
                
        # for getting package links
        soup        = BeautifulSoup(self.packageSource)
        contents    = soup.find("div", { "class" : "contents" })
        li          = contents.findAll("tr", {})
        
        self.packages = {}
        for i in li:
            if i.a["href"]:
                self.packages[i.a.text] = i.a["href"]
        print "Packages parsed(%d)..." % len(self.packages)

        # for getting items from file.html
        soup        = BeautifulSoup(self.filesSource)
        contents    = soup.find("div", { "class" : "contents" })
        tr          = contents.findAll("tr", {})
        self.classes= {}
        # depth of interface items can be only 3
        flag = False
        for i in tr:
            if self.__GetHTMLItemDepth(i) == 1:
                self.classes[i.text]    = {}
                level1          = i.text
                flag = False
                
            if self.__GetHTMLItemDepth(i) == 2:
                self.classes[level1][i.text] = {}
                level2 = i.text
                flag = False
            
            if self.__GetHTMLItemDepth(i) == 3 and i.text == u'interface':
                flag = True
            if self.__GetHTMLItemDepth(i) == 3 and i.text != u'interface':
                flag = False
                
            if flag and i.text != u'interface':
                self.classes[level1][level2][i.text] = i.a["href"]
                #self.ZEG = i
        print "Class hierarchy loaded(%d)..." % len(self.classes)
        
        # for parsing classes links from classes.html
        soup        = BeautifulSoup(self.classesSource)
        contents    = soup.find("div", { "class" : "contents" })
        td          = contents.findAll("td", {})
        self.classesURLs = {}
        # add items to self.classesURLs
        for i in td:
            if i.a and i.a.has_key('href'):
                self.classesURLs[i.a.text] = i.a['href']
        print "Class URLs was loaded... (%s)" % len(self.classesURLs)
        
        for i in self.data.keys():
            for j in self.data[i].keys():
                if not self.classes.has_key(j): continue
                for k in self.data[i][j].keys():
                    if "Package " + j + "/" + k in self.packages:
                        self.data[i][j][k]["__DATA__"]["packageDoc"] = '../' + self.packages["Package " + j + "/" + k]
                    if not self.classes[j].has_key(k): continue
                    for h in self.classes[j][k]:
                        if self.classesURLs.has_key(self.GetFileName(h)):
                            self.data[i][j][k][self.GetFileName(h)] = {"__DATA__": '../' + self.classesURLs[self.GetFileName(h)]}
                        else:
                            self.data[i][j][k][self.GetFileName(h) + ".h"] = {"__DATA__": '../' + self.classes[j][k][h]}

    def ExportJSON(self, fileName):
        if self.data == None:
            self.PrepareData()
        self.WriteFile(fileName, json.dumps(self.data, indent = 1))

    def CreateNewMainPage(self, outputFileName):
        if self.data == None:
            self.PrepareData()
            
        contents = """
        <table class="doctable" border="0" cellpadding="0" cellspacing="0">
        <tbody>
        <tr class="top" valign="top">
        <th class="domain">Domain</th><th class="contact">Contact</th>
        </tr>
        """
        keysI = self.data.keys()
        keysI.sort()
        for i in keysI:
            #########################
            if i == 'Other': continue
            
            self.__NewTreePage(i)
            contents = contents + '\n<tr class="DCRow">\n'    ######### TAG: TR1
            #########################
            if i == 'Operations':
                contents = contents + """<td width="50%%" style="padding:8px">%s</td>\n""" % i
            else:
                contents = contents + """<td width="50%%" style="padding:8px;cursor:pointer" onclick="toggleHoba('hoba_%s', 'iframes/%s.html')" id="hoba_%s"><a>%s</a></td>\n""" % (i.replace(' ', '_'), i.lower().replace(' ', '_'), i.replace(' ', '_'), i)
            #########################
            
            contents = contents + '<td width="50%" class="contact">'
            for j in range(len(self.data[i]["__DATA__"]["Contact"])):
                if j == len(self.data[i]["__DATA__"]["Contact"]) - 1:
                    contents = contents + '<a href="mailto:%s">%s</a> ' % (self.data[i]["__DATA__"]["Contact"][j][1], self.data[i]["__DATA__"]["Contact"][j][0])
                else:
                    contents = contents + '<a href="mailto:%s">%s</a>, ' % (self.data[i]["__DATA__"]["Contact"][j][1], self.data[i]["__DATA__"]["Contact"][j][0])
            contents = contents + '</td>\n'
            contents = contents + '</tr>\n\n'               ######### TAG: TR1
            #########################
            if i == 'Operations': continue
            #########################
            contents = contents + """
            <tr><td colspan="2" style="background:#d7dbe3">
            <div style="display:none;" id="hoba_%s_div"><iframe width="100%%" frameborder="0"></iframe></div>
            </td></tr>
            """ % (i.replace(' ', '_'))
            
        contents = contents + "</table>"
        self.WriteFile(outputFileName, self.mainPageTemplate.replace(self.contentStamp, contents))
    
    def __NewTreePage(self, domain):
        
        if not self.data.has_key(domain): return
        
        content = ''
        keysI = self.data[domain].keys()
        keysI.sort()
        for i in keysI:
            if i == '__DATA__': continue
            content += self.HTMLTreeBegin(i)
            keysJ = self.data[domain][i].keys()
            keysJ.sort()
            for j in keysJ:
#                if len(self.data[domain][i][j].keys()) == 1:
#                    if self.data[domain][i][j].has_key("__DATA__"):
#                        content += self.HTMLTreeAddItem(j, self.data[domain][i][j]["__DATA__"])
#                    else:
#                        content += self.HTMLTreeAddItem(j)
#                    continue
                keysK = self.data[domain][i][j].keys()
                keysK.sort()
                length = len(keysK)

                if length > 1:
                    if self.data[domain][i][j].has_key("__DATA__"):
                        content += self.HTMLTreeBegin(j, self.data[domain][i][j]["__DATA__"])
                    else:
                        content += self.HTMLTreeBegin(j)
                else:
                    if self.data[domain][i][j].has_key("__DATA__"):
                        content += self.HTMLTreeAddItem(j, self.data[domain][i][j]["__DATA__"], empty = True)
                    else:
                        content += self.HTMLTreeAddItem(j, empty = True)

                for k in keysK:
                    if k == '__DATA__': continue
                    if self.data[domain][i][j][k]["__DATA__"]: content += self.HTMLTreeAddItem(k, self.data[domain][i][j][k]["__DATA__"])
                    else: content += self.HTMLTreeAddItem(k)
            if length > 1:
                content += self.HTMLTreeEnd()
            content += self.HTMLTreeEnd()
        if self.tWikiLinks.has_key(domain):
            self.WriteFile("iframes/%s.html" % domain.lower().replace(' ', '_'), self.treePageTamplate % (domain, self.tWikiLinks[domain], content))
        else:
            print 'Warning: The twiki link of "%s" domain not found...' % domain
            self.WriteFile("iframes/%s.html" % domain.lower().replace(' ', '_'), self.treePageTamplate % (domain, '#', content))
    
    def HTMLTreeBegin(self, title, links = {}):
        html = '\n<li>\n<div class="hitarea expandable-hitarea"></div>\n'
        html = html + '<span class="folder">%s\n' % title
        for i in links.keys():
            html = html + '<a target="_blank" href="%s">[%s]</a> \n' % (links[i], i)
        html = html + '</span>\n'
        html = html + '<ul style="display: block;">\n'
        return html
    
    def HTMLTreeEnd(self):
        return '</li></ul>\n\n'
    
    def HTMLTreeAddItem(self, title, links = None, endNode = False, empty = False):
        if endNode: html = '\t<li class="last">'
        else: html = '\t<li>'
        
        if type(links) == str or type(links) == type(u''):
            if empty:
                html = html + '\t<a href="%s" target="_blank" class=""><span class="emptyFolder">%s</span></a>\n' % (links, title)
            else:
                html = html + '\t<a href="%s" target="_blank" class=""><span class="file">%s</span></a>\n' % (links, title)
        elif type(links) == dict:
            if empty:
                html = html + '<span class="emptyFolder">%s ' % title
            else:
                html = html + '<span class="file">%s ' % title
            for i in links.keys():
                html = html + '<a target="_blank" href="%s">[%s]</a> \n' % (links[i], i)
            html = html + '</span>'
        else:
            html = html + '\t<span class="file">%s</span>\n' % title
        return html + '\t</li>\n'
        