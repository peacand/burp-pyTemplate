# -*- coding: utf-8 -*-

# imports specific to Burp
from burp import IBurpExtender
from burp import IContextMenuFactory
from burp import ITab
from burp import IMessageEditorController

# python imports
import array
import os

# "java" imports
from java.io import PrintWriter
from javax.swing import JMenuItem
from javax.swing import JSplitPane
from javax.swing import JTextArea
from javax.swing import JScrollPane
from javax.swing import JPanel
from javax.swing import JButton
from javax.swing import JFileChooser
from java.awt import GridLayout
from java.awt import FlowLayout

class BurpExtender(IBurpExtender, ITab, IContextMenuFactory):

    #
    # implement IBurpExtender
    #

    def registerExtenderCallbacks(self, callbacks):
        
        # properties
        self._title = "Generate Python Template"
        self._templatePath = '###### ----> PUT HERE THE ABSOLUTE PATH TO template.py <--- ####'
        
        # set our extension name
        callbacks.setExtensionName(self._title)
        
        # keep a reference to our callbacks object
        self._callbacks = callbacks
        
        # obtain an extension helpers object
        self._helpers = callbacks.getHelpers()
        
        # obtain std streams
        self._stdout = PrintWriter(callbacks.getStdout(), True)
        self._stderr = PrintWriter(callbacks.getStderr(), True)
                
        # main pane (top/bottom)
        self._mainpane = JPanel()
        self._mainpane.setLayout( GridLayout(2,1) )
        
        # configure bottom pane for buttons
        self._botPane = JPanel()
        flowLayout = FlowLayout()
        self._botPane.setLayout( flowLayout )
        self._botPane.add( JButton("Generate", actionPerformed=self.regeneratePy) )
        self._botPane.add( JButton("Export", actionPerformed=self.exportPy) )
        
        # Configure pyViewer (JTextArea) for python output --> top pane
        self._pyViewer = JTextArea(5, 20);
        scrollPane = JScrollPane(self._pyViewer); 
        self._pyViewer.setEditable(True);
        self._pyViewer.setText( "Waiting request ..." );
        
        ### Assign top / bottom components
        self._mainpane.add(scrollPane)
        self._mainpane.add(self._botPane)
                
        # customize our UI components
        callbacks.customizeUiComponent(self._mainpane)
        
        # add the custom tab to Burp's UI
        callbacks.addSuiteTab(self)
        
        
        # register ourselves as a ContextMenuFactory
        callbacks.registerContextMenuFactory(self)
        
        return

    def regeneratePy(self,event):
        pass

    def exportPy(self,event):
        chooseFile = JFileChooser()
        ret = chooseFile.showDialog(self._mainpane, "Choose file")
        filename = chooseFile.getSelectedFile().getCanonicalPath()
        self._stdout.println("Export to : " + filename )
        open(filename, 'w', 0).write( self._pyViewer.getText() )


    #
    # implement ITab
    #
    
    def getTabCaption(self):
        return "PyTemplate"
    
    def getUiComponent(self):
        return self._mainpane


    #
    # implement IContextMenuFactory
    #

    def createMenuItems(self, invocation):
        # add a new item executing our action
        item = JMenuItem(self._title, actionPerformed=lambda x, inv=invocation: self.loadRequest(inv))
        return [ item ]

    def loadRequest(self, invocation):
        pyCode = self.pythonHeader()
        selectedMessages = invocation.getSelectedMessages()
        self._numbMessages = len(selectedMessages)
        self._currentMessageNumber = 1
        for message in selectedMessages:
            self._currentlyDisplayedItem = message
            pyCode += self.generateRequest()
            self._currentMessageNumber += 1
        pyCode += '\n' + self.generateMain()
        self._pyViewer.setText( pyCode );


    def pythonHeader(self):
        pyCode = "# -*- coding: utf-8 -*-\n\n"
        pyCode += "import requests\n"
        pyCode += "import time\n\n"
        return pyCode

    def formatHeaders(self, httpReqInfos):
        headers = httpReqInfos.getHeaders()[1:] #First header is method+path : GET/POST ..
        formatHeaders = ""

        name,content = headers[0].split(':', 1)
        formatHeaders += 'headers["' + self.sanitizeStr(name) + '"] = ' + '"' + self.sanitizeStr(content) + '"\n'

        for header in headers[1:]:
            name,content = header.split(':', 1)
            if "Content-Length" not in name:
                if "Cookie" in name and self._numbMessages > 1 and self._currentMessageNumber != 1:
                    continue
                else:
                    formatHeaders += '    headers["' + self.sanitizeStr(name) + '"] = ' + '"' + self.sanitizeStr(content) + '"\n'
        return formatHeaders


    def sanitizeStr(self, strToValid):
        valid = str(strToValid)
        valid = valid.replace('"','\\"')
        return valid.strip()

    def generateRequest(self):
        httpInfos = self._currentlyDisplayedItem.getHttpService()
        httpReq = self._currentlyDisplayedItem.getRequest()
        requestInfos = self._helpers.analyzeRequest(httpInfos, httpReq)
        pyTemplate = open(self._templatePath, 'r').read()
        pyCode = pyTemplate.replace( '$$NUM$$', str(self._currentMessageNumber) )
        pyCode = pyCode.replace( '$$URL$$', self.sanitizeStr(requestInfos.getUrl()) )
        pyCode = pyCode.replace( '$$HEADERS$$', self.formatHeaders(requestInfos) )
        pyCode = pyCode.replace( '$$METHOD$$', requestInfos.getMethod() )
        if requestInfos.getMethod() == "GET":
            trigger = "req = session.get(url, headers=headers, verify=False, allow_redirects=True)" 
            pyCode = pyCode.replace( '$$TRIGGER$$', trigger )
            pyCode = pyCode.replace( '$$POST_DATA$$', '' )
        if requestInfos.getMethod() == "POST":
            trigger = "req = session.post(url, headers=headers, data=post_data, verify=False, allow_redirects=True)" 
            pyCode = pyCode.replace( '$$TRIGGER$$', trigger )
            rawData = httpReq[requestInfos.getBodyOffset():].tostring()
            dataPyCode = '## POST DATA\n'
            dataPyCode += '    post_data = "' + self.sanitizeStr(rawData) + '"\n'
            pyCode = pyCode.replace( '$$POST_DATA$$', dataPyCode )
        return pyCode + '\n'

    def generateMain(self):
        pyCode = 'if __name__ == "__main__":\n'
        pyCode += '    session = requests.Session()\n'
        for i in xrange(1, self._numbMessages + 1):
            pyCode += '    code_'+str(i)+', time_'+str(i)+', response_'+str(i)+' = performRequest_'+str(i)+'(session)\n'
        return pyCode

