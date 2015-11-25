#!/bin/env python
import string
import re
import pyparsing

refactors = {"CO": {}, "IF": {}, "OP": {}, "DT": {}, "EX": {}}

class C(object):
    def __init__(self, name, superComp, description = ""):
        """
        Component klasse. Vul alles in dat in de template moet staan.
        description wordt geinterpreteerd als een template.
        """
        self._name = name
        self._superComp = superComp
        if superComp:
            superComp.addSub(self)
        self._subs = []
        self._interfaces = []
        self._description = string.Template(description)
    def getName(self):
        return self._name
    def getSubtypes(self):
        allTypes = {t for dts in [i.getSubtypes() for i in self._interfaces] for t in dts}
        return allTypes
    def refactor(self,oldName,newName):
        if self.getName() == oldName:
            self.setName(newName)
        return self
    def addSub(self, sub):
        self._subs.append(sub)
    def addInt(self, interface):
        self._interfaces.append(interface)
    def addDesc(self, description):
        self._description = description
    def refactorIF(self, oldName, newName):
        for inter in self._interfaces:
            if inter.getName() == oldName:
                inter.setName(newName)
    def refactorOp(self, oldName, newName):
        for inter in self._interfaces:
            inter.refactorOp(oldName,newName)
        return self
    def refactorDT(self, oldName, newName):
        for inter in self._interfaces:
            inter.refactorDT(oldName,newName)
        return self
    def refactorEx(self, oldName, newName):
        for inter in self._interfaces:
            inter.refactorEx(oldName,newName)
        return self
    def fillIn(self,template):
        s = self._superComp
        return template.substitute(selfN=self.getName()
                                  ,superN="eDocs" if not s else s.getName())
    def __str__(self):
        tmpl = string.Template("""
\\subsection{$name}
\\label{$name}
\\begin{itemize}
    \\item \\textbf{Description:} $description
    \\item \\textbf{Super-component:} $superC.
    \\item \\textbf{Sub-components:} $subCs.
\\end{itemize}

\\subsubsection*{Provided interfaces}
\\begin{itemize}$interfaces
\\end{itemize}""")
        return tmpl.substitute(name=self._name
                              ,superC="\\comp{"+self._superComp.getName()+"}" if self._superComp else "None"
                              ,subCs=", ".join("\\comp{"+sub.getName()+"}" for sub in self._subs) if self._subs else "None"
                              ,interfaces="".join(sorted(map(str,self._interfaces)))
                              ,description=self.fillIn(self._description))

class I:
    def __init__(self, name, components):
        """
        Interface klasse. Geef alles mee dat in de template ingevuld moet worden.
        Refactors worden doorgegeven naar lager niveau.
        """
        self._name = name
        self._component = components[0]
        components[0].addInt(self)
        if len(components) > 1:
            self._brother = I(name,components[1:])
        else:
            self._brother = None
        self._operations = []
    def setComp(self,component):
        self._component = component
        return self
    def getName(self):
        return self._name
    def setName(self, newName):
        self._name = newName
        return self
    def getSubtypes(self):
        allTypes = {t for dts in [o.getSubtypes() for o in self._operations] for t in dts}
        return allTypes
    def addOp(self, operation):
        self._operations.append(operation)
        if self._brother:
            return self._brother
        else:
            return None
    def refactorOp(self, oldName, newName):
        for op in self._operations:
            if op.getName() == oldName:
                op.setName(newName)
        if self._brother:
            self._brother.refactorOp(operation)
        return self
    def refactorDT(self, oldName, newName):
        for op in self._operations:
            op.refactorDT(oldName,newName)
        if self._brother:
            self._brother.refactorDT(operation)
        return self
    def refactorEx(self, oldName, newName):
        for op in self._operations:
            op.refactorEx(oldName,newName)
        if self._brother:
            self._brother.refactorEx(operation)
        return self
    def __str__(self):
        tmpl = string.Template("""
    \\item $name
    \\begin{itemize}$operations
    \\end{itemize}""")
        return tmpl.substitute(name=self._name,operations="".join(sorted(map(str,self._operations))))

class O:
    def __init__(self, name, interface, returnType, paramTypes, exceptions = [], effect = "", exceptConds = [], additionalInfo = {}):
        """
        Operation klasse. Geef alles mee dat in de template ingevuld moet worden.
        effect en alle items in exceptConds worden geinterpreteerd als template strings.
        """
        self._name = name
        if isinstance(interface,list):
            self._interface = interface[0]
        else:
            self._interface = interface
        self._additionalInfo = additionalInfo
        self._returnType = returnType
        self._paramTypes = paramTypes if paramTypes else []
        # defaultwaarden
        self._paramNames = {s:self.namify(s) for s in self._paramTypes}
        self._exceptions = exceptions if exceptions else []
        # _exceptConds wordt {} als exceptions of exceptConds [] is. {} is ook Falsy
        self._exceptConds = {e:string.Template(exceptConds[exceptions.index(e)])
                for e in self._exceptions} if exceptConds else {}
        self._effect = string.Template(effect)
        if isinstance(interface,list):
            uncle = interface[0].addOp(self)
            if uncle:
                self._cousin = O(name,uncle,returnType,paramTypes,exceptions,effect,exceptConds,additionalInfo)
            else:
                self._cousin = None
            if len(interface) > 2:
                self._brother = O(name,interface[1:],returnType,paramTypes,exceptions,effect,exceptConds,additionalInfo)
            else:
                self._brother = O(name,interface[1],returnType,paramTypes,exceptions,effect,exceptConds,additionalInfo)
        else:
            uncle = interface.addOp(self)
            if uncle:
                self._cousin = O(name,uncle,returnType,paramTypes,exceptions,effect,exceptConds,additionalInfo)
            else:
                self._cousin = None
            self._brother = None
    def getName(self):
        return self._name
    def setName(self,newName):
        self._name = newName
        if self._cousin:
            self._cousin.setName(newName)
        return self
    def getSubtypes(self):
        def subTypes(strOrComposite):
            if isinstance(strOrComposite,str):
                return [strOrComposite]
            else:
                level1 = strOrComposite.getSubtypes()
                plains = list(filter(lambda t: isinstance(t,str),level1))
                others = filter(lambda t: not isinstance(t,str),level1)
                return plains+[st for t in others for st in t.getSubtypes()]
        raw = [self._returnType]+self._paramTypes
        cooked = {t for rt in raw for t in subTypes(rt)}
        return cooked
    def changeParamName(self,paramType,newName):
        self._paramNames[paramType] = newName
        if self._cousin:
            self._cousin.changeParamName(paramType,newName)
        return self
    def namify(self,paramName,front = True):
        def frontify(s):
            return s[0].lower()+s[1:]
        if isinstance(paramName,str):
            return frontify(paramName) if front else paramName
        if isinstance(paramName,ListT):
            ret = self.namify(paramName.getSubtypes()[0],front = False)+"s"
            return frontify(ret) if front else ret
        if isinstance(paramName,TupleT):
            ret = "And".join(map(lambda s: self.namify(s,front = False), paramName.getSubtypes()))
            return frontify(ret) if front else ret
        if isinstance(paramName,MapT):
            ret = "For".join(map(lambda s: self.namify(s,front = False), reversed(paramName.getSubtypes())))
            return frontify(ret) if front else ret
        else:
            return str(paramName)
    def refactorDT(self,oldName,newName):
        #TODO family
        if self._returnType == oldName:
            self._returnType = newName
        self._paramTypes = [newName if t == oldName else t for t in self._paramTypes]
        self._paramNames = {(newName if t == oldName else t):self._paramNames[t]
                            for t in self._paramNames}
        return self
    def refactorEx(self,oldName,newName):
        #TODO family
        self._exceptions = [newName if e == oldName else e for e in self._exceptions]
        self._exceptConds = {(newName if e == oldName else e):self._exceptConds[e]
                             for e in self._exceptConds}
        return self
    def changeExceptCond(self,exception,newCondition):
        self._exceptConds[self._exceptions.index(exception)] = newCondition
        if self._cousin:
            self._cousin.changeExceptCond(exception,newCondition)
        return self
    def formatExcepts(self):
        def appropriateCond(e):
            approp = ""
            if e in self._exceptConds and self._exceptConds[e]:
                approp = ": " + self.fillIn(self._exceptConds[e])
            else:
                approp = ": %TODO"
            return approp
        return [e + appropriateCond(e) for e in self._exceptions]
    def fillIn(self,template):
        def datatypify(dt):
            if isinstance(dt,str):
                return "\\dt{"+dt+"}"
            else:
                return str(dt)
        interface = self._interface
        component = self._interface._component
        paramTs = self._paramTypes
        paramNs = [self._paramNames[pt] for pt in paramTs]
        exceptTs = self._exceptions
        additional = {} if not self._additionalInfo else self._additionalInfo[self._interface._component.getName()]
        return template.substitute(selfN=self.getName()
                                  ,interN="\\texttt{"+interface.getName()+"}"
                                  ,compN="\\comp{"+component.getName()+"}"
                                  ,returnT=datatypify(self._returnType)
                                  ,**dict({"{0}{1}{2}".format(elem[0],elem[1],elem[2]):
                                      datatypify(elem[3])
                                      for elem in
                                        [("param",i[0],"T",i[1]) for i in enumerate(paramTs)] +
                                        [("param",i[0],"N",i[1]) for i in enumerate(paramNs)] +
                                        [("except",i[0],"T",i[1]) for i in enumerate(exceptTs)]},**additional))
    def __str__(self):
        tmpl = string.Template("""
        \\item \\texttt{$returnType $name($params) $excepts}
        \\begin{itemize}
            \\item Effect: $effect
            \\item Exceptions:
            \\begin{itemize}$exceptitems
            \\end{itemize}
        \\end{itemize}""")
        return tmpl.substitute(name=self._name
                              ,returnType=self._returnType
                              ,params=", ".join(str(p) + " " + self._paramNames[p] for p in self._paramTypes) if self._paramTypes else ""
                              ,excepts=("throws " if self._exceptions else "") + ", ".join(map(str,self._exceptions))
                              ,effect=self.fillIn(self._effect)
                              ,exceptitems=("\n                \\item " + """
                \\item """.join(self.formatExcepts())) if self._exceptions else "\n                \\item None")

class TupleT:
    def __init__(self,dts):
        self._subTypes = dts
    def __eq__(self,other):
        return isinstance(other,self.__class__) and self._subTypes == other._subTypes
    def __hash__(self):
        return hash(tuple(self._subTypes))
    def __str__(self):
        return "Tuple<"+",".join(
                map(lambda st:
                      "\dt{"+st+"}" if isinstance(st,str)
                      else str(st)
                    ,self._subTypes))+">"
    def getSubtypes(self):
        return self._subTypes
class ListT:
    def __init__(self,dt):
        self._subType = dt
    def __eq__(self,other):
        return isinstance(other,self.__class__) and self._subType == other._subType
    def __hash__(self):
        return hash((1,self._subType))
    def __str__(self):
        st = self._subType
        return "List<"+("\dt{"+st+"}" if isinstance(st,str) else str(self._subType))+">"
    def getSubtypes(self):
        return [self._subType]
class MapT:
    def __init__(self,dt1,dt2):
        self._subTypes = [dt1,dt2]
    def __eq__(self,other):
        return isinstance(other,self.__class__) and self._subTypes == other._subTypes
    def __hash__(self):
        return hash(tuple(self._subTypes))
    def __str__(self):
        return "Map<"+",".join(
                map(lambda st:
                      "\dt{"+st+"}" if isinstance(st,str)
                      else str(st)
                    ,self._subTypes))+">"
    def getSubtypes(self):
        return self._subTypes

### COMPONENT STRUCTURE ###

cf=C("CustomerFacade",None)
dbf=C("DashboardFacade",cf)
crh=C("CustomerRegistrationHandler",cf)
cah=C("CustomerAuthenticationHandler",cf)
tm=C("TemplateManager",cf)
fsc=C("FirstStatusCache",cf)
ssc=C("SecondStatusCache",cf)
cdb=C("CustomerDB",cf)
ofcdb=C("OtherFunctionalityCDB",cdb)
srm=C("StatusReplicationManager",cdb)
sdbr=C("StatusDBReplica",cdb)
rf=C("RecipientFacade",None)
rs=C("RecipientScheduler",rf)
drh=C("DocumentRequestHandler",rf)
rg=C("RecipientGateway",rf)
rdb=C("RecipientDB",rf)
rah=C("RecipientAuthenticationHandler",rf)
poh=C("PDSOverviewHandler",drh)
psh=C("PDSSearchHandler",drh)
dlh=C("DocumentLookupHandler",drh)
rdf=C("RawDataFacade",None)
dgh=C("DocumentGenerationHandler",None)
dgm=C("DocumentGenerationManager",None)
tc=C("TemplateCache",dgm)
kc=C("KeyCache",dgm)
com=C("Completer",dgm)
sch=C("Scheduler",dgm)
gm=C("GeneratorManager",dgm)
pdsdb=C("PDSDB",None)
pltdm=C("PDSLongTermDocumentManager",pdsdb)
prm=C("PDSReplicationManager",pdsdb)
pdsr=C("PDSDBReplica",pdsdb)
pdsc=C("PDSCache",None)
gen=C("Generator",None)
dsf=C("DeliveryServiceFacade", None)
dc=C("DeliveryCache",dsf)
dh=C("DeliveryHandler",dsf)
zdh=C("ZoomitDeliveryHandler",dsf)
pdh=C("PostalDeliveryHandler",dsf)
edh=C("EMailDeliveryHandler",dsf)
nh=C("NotificationHandler",None)
can=C("CustomerAdminNotifier",nh)
ean=C("EDocsAdminNotifier",nh)
nd=C("NotificationDistributor",nh)

components=[cf,dbf,crh,cah,tm,fsc,ssc,cdb,ofcdb,srm,sdbr,rf,rs,drh,rg,rdb,rah,poh,psh,dlh,rdf,dgh,dgm,tc,kc,com,sch,gm,pdsdb,pltdm,prm,pdsr,pdsc,gen,dsf,dc,dh,zdh,pdh,edh,nh,can,ean,nd]
cs = { comp.getName():comp for comp in components }

interfaces = [
        I("UseManagementDashboard",
          [cf, dbf]),
        I("Authentication",
          [cf, dbf, rf, rg]),
        I("CAuthentication",
          [cah]),
        I("RAuthentication",
          [rah]),
        I("CustomerRegistration",
          [cf, dbf]),
        I("ICustomerRegistration",
          [crh]),
        I("TemplateMgmt",
          [tm, dgh]),
        I("CustomerDataMgmt",
          [cdb, ofcdb]),
        I("DocumentStatus",
          [fsc, ssc, cdb, srm]),
        I("QueryCustomerInfo",
          [cf, cdb, ofcdb]),
        I("StatusReport",
          [srm]),
        I("StatusMgmt",
          [sdbr, cf, fsc, ssc, cdb, srm, dgh]),
        I("Ping",
          [sdbr, can, gen, pdsr]),
        I("UsePDS",
          [rf, rg]),
        I("DownloadDoc",
          [rf, rg]),
        I("RecipientRegistration",
          [rf, rg]),
        I("SetModus",
          [rf, rg, dgh]),
        I("PDSOperationHandling",
          [rs]),
        I("PDSLookupHandling",
          [dlh, drh]),
        I("PDSSearchHandling",
          [psh, drh]),
        I("PDSOverviewHandling",
          [poh, drh]),
        I("RecipientDataMgmt",
          [rdb]),
        I("QueryRecipients",
          [rf,rdb]),
        I("DeliverDocument",
          [dsf, dh, zdh, pdh, edh]),
        I("DeliveryCacheMgmt",
          [dc]),
        I("DeliverNotification",
          [dsf, edh]),
        I("NotifyDelivery",
          [dsf, zdh]),
        I("NotifyFailure",
          [dsf, edh]),
        I("InsertJobs",
          [dgm, sch]),
        I("GetStatistics",
          [sch]),
        I("GetNextJobs",
          [sch]),
        I("NotifyCompleted",
          [dgm, gm]),
        I("GetTemplate",
          [tc, dgh]),
        I("GetKey",
          [kc, dgh]),
        I("Complete",
          [com]),
        I("AssignJobs",
          [gen]),
        I("Startup/Shutdown",
          [gen]),
        I("NotifyOperator",
          [nh, nd]),
        I("NotifyCustomerAdmin",
          [nd]),
        I("NotifyEDocsAdmin",
          [nh, ean]),
        I("SendDataBatch",
          [rdf]),
        I("RawDataCommunication",
          [rdf]),
        I("RawDataMgmt",
          [dgh, pdsdb, prm, pdsr]),
        I("KeyMgmt",
          [dgh]),
        I("GetBatchData",
          [dgh]),
        I("FinalizeDocument",
          [dgh]),
        I("DocumentCacheMgmt",
          [pdsc]),
        I("DocumentMgmt",
          [pdsdb, pltdm]),
        I("PDSQuery",
          [pdsdb,pltdm]),
        I("ExtendedDocumentMgmt",
          [prm, pdsr]),
        I("GenerateUniqueLink",
          [rf, rg])
    ]

ifs = { inter.getName():inter for inter in interfaces }

operations = [
        # UseManagementDashboard
        O("consultManagementDashboard",
          ifs["UseManagementDashboard"],
          "DashboardOverview",
          ["AuthenticationToken"],
          ["AuthenticationException"],
          "The $compN will fetch the statuses of the most recently initiated documents of the customer organization identified by the given $param0T. These statuses will then be returned as a $returnT.",
          ["Thrown if no customer organization is associated with the given $param0T"]),
        O("changeDocumentTemplate",
          ifs["UseManagementDashboard"],
          "void",
          ["AuthenticationToken","DocumentType","Template"],
          ["AuthenticationException",
           "InvalidTypeException"],
           "The $compN will save the given $param2T as template for documents of type $param1N generated by the customer organization identified by the given $param0T. When a template of this type already existed for this organization, then this template is replaced by $param2N.",
           ["Thrown if no customer organization is associated with the given $param0T",
            "Thrown if the customer organization identified by $param0T does not support documents of type $param1N."]),
        O("consultTemplates",
          [ifs["UseManagementDashboard"],ifs["TemplateMgmt"]],
          ListT(TupleT(["DocumentType","Template"])),
          ["AuthenticationToken"],
          ["AuthenticationException"],
          "The $compN will return all document types generated by the customer organization identified by the given $param0T and their corresponding templates.",
          ["Thrown if no customer organization is associated with the given $param0T."]),
        O("consultBillingInfo",
          ifs["UseManagementDashboard"],
          "BillingInformation",
          ["AuthenticationToken"],
          ["AuthenticationException"],
          "The $compN will fetch billing information of the Customer Organization belonging to the given $param0T. This information is fetched from the \\comp{OtherFunctionalityCDB}.",
          ["Thrown if the given token is not associated with a Customer Administrator or if this Administrator is not authorized to consult billing information. Checking whether the token is valid happens in the \\comp{CustomerAuthenticationHandler}."]),
        O("sendDataBatch",
          ifs["UseManagementDashboard"],
          "void",
          ["AuthenticationToken",ListT(TupleT(["Metadata","RawData"]))],
          ["AuthenticationException","InvalidDataException"],
          "It is possible to use the Management Dashboard to send in a new Raw Data Batch. The Batch is then passed to the \\comp{RawDataFacade} which checks the data format for errors.",
          ["If the provided $param0T is invalid an $except0T is thrown.","If any of the Raw Data or Metadata is syntactically incorrect or in an incorrect format the \\comp{RawDataFacade} throws an $except0T which is then passed on to the Customer Administrator using the Management Dashboard through the $compN."]),
        # Authentication
        O("logIn",
          ifs["Authentication"],
          "AuthenticationToken",
          ["Credentials"],
          ["InvalidCredentialsException"],
          "The $compN will forward the given $param0T to the $handler which will authenticate them and return an $returnT. This token can then be used for further requests to the $service.",
          ["Thrown when the given credentials are incorrect, which is indicated by the $handler."],
          {"RecipientGateway": {"handler": "\\comp{RecipientAuthenticationHandler}", "service": "PDS"}
          ,"RecipientFacade": {"handler": "\\comp{RecipientGateway}", "service": "PDS"}
          ,"CustomerFacade": {"handler": "\\comp{DashboardFacade}", "service": "Management Dashboard"}
          ,"DashboardFacade": {"handler": "\\comp{CustomerAuthenticationHandler}", "service": "Management Dashboard"}}),
        O("logOut",
          ifs["Authentication"],
          "void",
          ["AuthenticationToken"],
          None,
          "The $compN will use the $handler to remove the given $param0T, which means that this token can no longer be used to consult the $service.",
          ["Thrown if the given token is not associated with a Customer Administrator."],
          {"RecipientGateway": {"handler": "\\comp{RecipientAuthenticationHandler}", "service": "PDS"}
          ,"RecipientFacade": {"handler": "\\comp{RecipientGateway}", "service": "PDS"}
          ,"CustomerFacade": {"handler": "\\comp{DashboardFacade}", "service": "Management Dashboard"}
          ,"DashboardFacade": {"handler": "\\comp{CustomerAuthenticationHandler}", "service": "Management Dashboard"}}),
        # CAuthentication
        O("logIn",
          ifs["CAuthentication"],
          "AuthenticationToken",
          ["Credentials"],
          ["InvalidCredentialsException"],
          "The $compN will authenticate the Customer Administrator based on the given $param0T and return an $returnT. To do this the $compN queries the \\comp{OtherFunctionalityCDB} for the correct $param0T and compares them. This token can then be used for further requests to the Management Dashboard.",
          ["Thrown when the given credentials are incorrect."]),
        O("logOut",
          ifs["CAuthentication"],
          "void",
          ["AuthenticationToken"],
          None,
          "The $compN will remove the given $param0T, which means that this token can no longer by used to consult the Management Dashboard.",
          ["Thrown if the given token is not associated with a Customer Administrator."]),
        O("idForToken",
          ifs["CAuthentication"],
          "CustomerID",
          ["AuthenticationToken"],
          ["InvalidArgumentException"],
          "The $compN returns the $returnT associated with the given $param0T (if such an ID exists, otherwise an $except0T is thrown)",
          ["Thrown if the provided $param0T is not found"]),
        # RAuthentication
        O("logIn",
          ifs["RAuthentication"],
          "AuthenticationToken",
          ["Credentials"],
          ["InvalidCredentialsException"],
          "The $compN will authenticate the given $param0T and return an $returnT. To do this the $compN queries the \\comp{RecipientDB} for the correct $param0T and compares them. This token can then be used for further requests to the $compN.",
          ["Thrown when the given credentials are incorrect."]),
        O("logOut",
          ifs["RAuthentication"],
          "void",
          ["AuthenticationToken"],
          None,
          "The $compN will remove the given $param0T, which means that this token can no longer by used to consult the Personal Document Store.",
          ["Thrown if the given token is not associated with a Recipient."]),
        O("idForToken",
          ifs["RAuthentication"],
          "RecipientID",
          ["AuthenticationToken"],
          ["InvalidArgumentException"],
          "The $compN returns the $returnT associated with the given $param0T (if such an ID exists, otherwise an $except0T is thrown)",
          ["Thrown if the given token is not associated with a Recipient."]),
        # CustomerRegistration
        O("registerCustomer",
          ifs["CustomerRegistration"],
          "void",
          ["AuthenticationToken",ListT("Credentials"),"RawDataCredentials","CustomerContactDetails","DocumentKey","SLA",MapT("DocumentType","Template")],
          ["AuthenticationException","InvalidArgumentException"],
          "The $compN will check wether the given $param0T is associated with the eDocs Administrator. If this is the case, the $compN will forward the given $param1N, $param3N, $param4N and $param5T to the \\comp{CustomerRegistrationHandler} and the $param2T to the \\comp{RawDataFacade}. The $param2T can be anything that identifies a "
          + "Customer Organization, like a username and password or a public key, used for safe transfer of Raw Data Batches to the \\comp{RawDataFacade}.",
          ["Thrown if the given token is not associated with the eDocs Administrators. Only an administrator can register a new company.",
           "Thrown if there is already a Customer Organization associated with the given $param3T $param3N or credentials (either $param1N or $param2N)."]).changeParamName(
                   ListT("Credentials"),"customerCredentials").changeParamName(
                           "AuthenticationToken","eDocsAdminToken"),
        O("unregisterCustomer",
          ifs["CustomerRegistration"],
          "UnregistrationToken",
          ["AuthenticationToken","CustomerID"],
          ["AuthenticationException"],
          "The $compN will check whether the given $param0T is associated with the eDocs Administrator. If this is the case, the $compN will forward the given $param1T to the \\comp{CustomerRegistrationHandler}, which will mark that the Customer Organization associated with the given $param1T needs to be unregistered. An $returnT is then returned by the \\comp{CustomerRegistrationHandler}, which is in turn returned by the $compN. This $returnT can then be used to confirm the unregistration of the Customer Organization.",
          ["Thrown if the given token is not associated with the eDocs Administrators. Only an administrator can unregister a company."]).changeParamName(
                  "AuthenticationToken","eDocsAdminToken"),
        O("confirmUnregistration",
          ifs["CustomerRegistration"],
          "Boolean",
          ["UnregistrationToken"],
          None,
          "The $compN will forward the given $param0T to the \\comp{CustomerRegistrationHandler}, which will confirm the unregistration. That Customer Organization can no longer send in Raw Data Batches or log in to the Management Dashboard. A boolean is then returned, indicating whether the unregistration has succeeded or not."),
        # ICustomerRegistration
        O("registerCustomer",
          ifs["ICustomerRegistration"],
          "CustomerID",
          [ListT("Credentials"),"CustomerContactDetails","DocumentKey","SLA"],
          ["InvalidArgumentException"],
          "The $compN will use the \\comp{OtherFunctionalityCDB} to save the given $param0T, $param1T, $param2T and $param3T. The $param3T also includes whether or not the Customer Organization has enabled receipt tracking.",
          ["Thrown if the provided $param0T $param0N or $param1T $param1N are already associated with a Customer Organization"]).changeParamName(
                  ListT("Credentials"),"customerCredentials"),
        O("unregisterCustomer",
          ifs["ICustomerRegistration"],
          "UnregistrationToken",
          ["CustomerID"],
          ["InvalidArgumentException"],
          "The $compN will forward the given $param0T to the \\comp{CustomerRegistrationHandler}, which will mark that the Customer Organization associated with the given $param0T needs to be unregistered. An $returnT is then returned by the \\comp{CustomerRegistrationHandler}, which is in turn returned by the $compN. This $returnT can then be used to confirm the unregistration of the Customer Organization.",
          ["Thrown if the given token is not associated with the eDocs Administrators. Only an administrator can unregister a company."]),
        O("confirmUnregistration",
          ifs["ICustomerRegistration"],
          "Boolean",
          ["UnregistrationToken"],
          None,
          "The unregistration of the Customer Organization associated with $param0N is confirmed. That Customer Organization can no longer send in Raw Data Batches or log in to the Management Dashboard. A boolean is then returned, indicating whether the unregistration has succeeded or not."),
        # TemplateMgmt: zie UseManagementDashboard
        # CustomerDataMgmt
        O("consultBillingInfo",
          ifs["CustomerDataMgmt"],
          "BillingInformation",
          ["CustomerID"],
          None,
          "The \\comp{OtherFunctionalityCDB} will fetch a report of statuses of recent documents (sent by the Customer Organization associated with the given $param0T) from the \\comp{StatusReplicationManager}. Billing information is then obtained by taking into account the recurring and non-recurring batches. The price of recurring batches is included in the SLA, stored in the $compN, and the price of the documents belonging to non-recurring batches depends on the priority of that document. Default priority is also included in the SLA."),
        O("registerCustomer",
          ifs["CustomerDataMgmt"],
          "CustomerID",
          ["Credentials","CustomerContactDetails","SLA"],
          ["InvalidArgumentException"],
          "The $compN saves the provided $param0T $param0N, $param1T $param1N, and $param2T $param2N in its internal data store. A new $returnT is assigned for this Customer Organization and immediately returned.",
          ["If the provided $param0T or $param1T were already used for a Customer Organization registration the registration request cannot be executed and the operation fails."]),
        O("getCredentials",
          ifs["CustomerDataMgmt"],
          TupleT(["Credentials","CustomerID"]),
          ["UserName"],
          None,
          "The $compN will return the credentials identified by the given $param0N and also the associated \\texttt{CustomerID}."),
        # DocumentStatus
        O("consultNumberOfStatuses",
          ifs["DocumentStatus"],
          ListT("DocumentStatus"),
          ["CustomerID","Integer"],
          ["OutOfRangeException"],
          "The $compN provides the statuses of the documents initiated by the Customer Organization belonging to the given $param0T. Only the last $param1N statuses added to this component are returned.",
          ["Thrown when the given integer is larger than the total number of statuses saved in the $compN."]).changeParamName(ListT("DocumentStatus"),"documentStatuses"),
        # QueryCustomerInfo
        O("queryRecurringBatchSize",
          ifs["QueryCustomerInfo"],
          "Integer",
          ["CustomerID"],
          None,
          "The $compN will return the size of recurring batches, according to the SLA of the Customer Organization belonging to the given $param0T."),
        O("queryRecurringBatchDeadline",
          ifs["QueryCustomerInfo"],
          "TimeStamp",
          ["CustomerID"],
          None,
          "The $compN will return the $returnT of the deadline for recurring batches. This is a part of the SLA of the Customer Organization belonging to the given $param0T."),
        O("queryDefaultPriority",
          ifs["QueryCustomerInfo"],
          "Priority",
          ["CustomerID"],
          None,
          "The $compN will return the default priority as specified in the SLA of the Customer Organization belonging to the given $param0T."),
        O("queryPrintParameters",
          ifs["QueryCustomerInfo"],
          "PrintParameters",
          ["CustomerID"],
          None,
          "The $compN will return the print parameters required for documents that need to be printed. These are a part of the SLA of the Customer Organization belonging to the given $param0T."),
        O("queryCustomerAdminContactDetails",
          ifs["QueryCustomerInfo"],
          "Credentials",
          ["CustomerID","DocumentType"],
          None,
          "Returns the $returnT for the Customer Administrator belonging to the department that requires the generation of the document type $param1N. If no such administrator is known the first administrator in the list is returned."),
        O("queryReceiptTracking",
          ifs["QueryCustomerInfo"],
          "Boolean",
          ["CustomerID"],
          None,
          "Returns a boolean value that represents whether or not the Customer Organization has enabled receipt tracking."),
        # StatusMgmt
        O("setStatus",
          ifs["StatusMgmt"],
          "void",
          ["DocumentStatus","DocumentID"],
          None,
          "The $compN will save the given $param0T of the document belonging to the given $param1T."),
        # StatusReport
        O("getStatusReport",
          ifs["StatusReport"],
          MapT("DocumentID","DocumentStatus"),
          ["CustomerID","TimeStamp"],
          None,
          "The $compN will look up documents sent by the Customer Organization with given $param0T and saved since the given $param1T. The $compN will return a map with the \\texttt{DocumentID} as key and the status of these documents as value. Also, only non-recurring Batches are considered. This way, the status report can easily be used to calculate billing information, since non-recurring batches need to be billed separately. Recurring batches are billed automatically."),
        # Ping
        O("ping",
          ifs["Ping"],
          "Echo",
          None,
          None,
          "The $compN will return an $returnT message to indicate that it has not failed. This way, the calling component can check the availability of the $compN."),
        # UsePDS
        O("getPDSOverview",
          ifs["UsePDS"],
          "PDSOverview",
          ["AuthenticationToken"],
          ["AuthenticationException"],
          "The $compN will look up which Recipient is associated with the given $param0T in the \\comp{RecipientAuthenticationHandler} and will then return an overview of the Personal Document Store of this Recipient. This overview contains a description of recently received documents of the Recipient and is obtained by calling the \\comp{RecipientScheduler}.",
          ["Thrown if no Recipient is associated with the given $param0T. Checking whether the token is valid happens in the \\comp{RecipientAuthenticationHandler}."]),
        O("consultDocument",
          ifs["UsePDS"],
          "DocumentOverview",
          ["AuthenticationToken","DocumentID"],
          ["AuthenticationException"],
          "The $compN will look up which \\texttt{RecipientID} is associated with the given $param0T in the \\comp{RecipientAuthenticationHandler} and will then return an overview of the document belonging to the given $param1T. This document was sent to the Recipient identified by the \\texttt{RecipientID}.",
          ["Thrown if no Recipient is associated with the given $param0T. Checking whether the token is valid happens in the \\comp{RecipientAuthenticationHandler}."]),
        O("searchDocuments",
          ifs["UsePDS"],
          ListT("DocumentOverview"),
          ["AuthenticationToken","DocumentQuery"],
          ["AuthenticationException"],
          "The $compN will use the \\comp{RecipientScheduler} to fetch the results of the given query $param1N, which needs to be performed on the personal document store of the Recipient associated with the given $param0T. A list of overviews of the documents resulting from this query is then returned. The Recipient is found by looking up the given token in the \\comp{RecipientAuthenticationHandler}.",
          ["Thrown if no Recipient is associated with the given $param0T. Checking whether the token is valid happens in the \\comp{RecipientAuthenticationHandler}."]),
        O("downloadDocument",
          ifs["UsePDS"],
          "Document",
          ["AuthenticationToken","DocumentID"],
          ["AuthenticationException"],
          "The $compN will first look up which recipient belongs to the given $param0T in the \\comp{RecipientAuthenticationHandler}. Then the $compN will use the \\comp{RecipientScheduler} to fetch the document belonging to the given $param1T.",
          ["Thrown if no recipient is associated with the given $param0T. Checking whether the token is valid happens in the \\comp{RecipientAuthenticationHandler}."]),
        # DownloadDoc
        O("downloadDocument",
          ifs["DownloadDoc"],
          "Document",
          ["UniqueDocumentToken"],
          ["InvalidTokenException","TokenExpiredException"],
          "The $compN will first look up which \\texttt{DocumentID} is associated with the given $param0T and will use this ID to fetch the actual $returnT from the \\comp{RecipientScheduler}.",
          ["Thrown if no document is associated with the given token.",
           "Thrown if a document was associated with the given token, but that this token has expired."]),
        # RecipientRegistration
        O("registerRecipient",
          ifs["RecipientRegistration"],
          TupleT(["Credentials","AuthenticationToken"]),
          ["RecipientContactDetails"],
          ["InvalidArgumentException"],
          "The $compN will use the \\comp{RecipientDB} to save the given $param0T. The \\comp{RecipientGateway} will then generate new \\dt{Credentials} for the Recipient that they can use to log in to the Personal Document Store and use the \\comp{RecipientAuthenticationHandler} to generate an \\dt{AuthenticationToken} that can be used to log in immediately after registering.",
          ["Thrown if there already exists a Recipient registered with the given e-mail address (which is part of the given $param0T). This is checked in the \\comp{RecipientDB}."]),
        O("unregisterRecipient",
          ifs["RecipientRegistration"],
          "UnregistrationToken",
          ["AuthenticationToken"],
          ["AuthenticationException"],
          "The $compN will use the \\comp{RecipientAuthenticationHandler} to look up the \\texttt{RecipientID} that is associated with the given $param0T. This ID will then be used to mark that the Recipient wants to unregister (from his/her Personal Document Store) by associating it with an $returnT. This $returnT is then returned, which can be used later to confirm the unregistration.",
          ["Thrown if no Recipient is associated with the given $param0T. This is checked in the \\comp{RecipientAuthenticationHandler}."]),
        O("confirmUnregistration",
          ifs["RecipientRegistration"],
          "Boolean",
          ["UnregistrationToken"],
          None,
          "The $compN will first check which Recipient is associated with given $param0T. The $compN will then use the \\comp{RecipientDB} to delete all contact details associated with this Recipient. The unregistration is confirmed (or not) by returning a boolean value which represents whether or not the unregistration succeeded."),
        # SetModus
        O("setDegraded",
          ifs["SetModus"],
          "void",
          [],
          None,
          # Effect hangt af van component!
          "The $compN will switch to degraded modus."),
        O("setNormal",
          ifs["SetModus"],
          "void",
          [],
          None,
          "The $compN will switch back from degraded modus to normal modus."),
        # PDSOperationHandling, PDSLookupHandling, PDSSearchHandling, PDSOverviewHandling, PDSQuery
        O("getPDSOverview",
          [ifs["PDSOperationHandling"],ifs["PDSOverviewHandling"],ifs["PDSQuery"]],
          ListT("DocumentOverview"),
          ["RecipientID"],
          None,
          "The $compN will return an overview of the Personal Document Store of the Recipient associated with the given $param0T. This overview contains a description of recently received documents of the Recipient."),
        O("consultDocument",
          [ifs["PDSOperationHandling"],ifs["PDSLookupHandling"],ifs["PDSQuery"]],
          "DocumentOverview",
          ["RecipientID","DocumentID"],
          None,
          "The $compN will return an overview of the document belonging to the given $param1T. This document was sent to the Recipient associated with the given $param0T."),
        O("searchDocuments",
          [ifs["PDSOperationHandling"],ifs["PDSSearchHandling"],ifs["PDSQuery"]],
          ListT("DocumentOverview"),
          ["RecipientID","DocumentQuery"],
          None,
          "The $compN will return an overview of the documents satisfying the given $param1T. These documents were sent to the Recipient associated with the given $param0T."),
        O("downloadDocument",
          [ifs["PDSOperationHandling"],ifs["PDSLookupHandling"],ifs["PDSQuery"]],
          "Document",
          ["RecipientID","DocumentID"],
          None,
          "The $compN will return the document associated with the given $param1T. This document was sent to the Recipient identified by given $param0T."),
        # RecipientDataMgmt
        O("getCredentials",
          ifs["RecipientDataMgmt"],
          TupleT(["Credentials","RecipientID"]),
          ["UserName"],
          None,
          "The $compN will return the \\texttt{Credentials} belonging to the Recipient with given $param0T, along with its \\texttt{RecipientID}."),
        O("registerRecipient",
          ifs["RecipientDataMgmt"],
          "void",
          ["Credentials","RecipientContactDetails"],
          ["InvalidArgumentException"],
          "The $compN will save the given $param0T and $param1T.",
          ["If the provided $param0T are already in use the $compN throws an $except0T."]),
        O("unregisterRecipient",
          ifs["RecipientDataMgmt"],
          "Boolean",
          ["RecipientID"],
          None,
          "The $compN will remove the account information related to the Recipient with $param0T $param0N. From now on the account corresponding to $param0N can no longer be used."),
        # QueryRecipients
        O("usesPDS",
          ifs["QueryRecipients"],
          "Boolean",
          ["EMailAddress"],
          None,
          "The $compN returns a boolean value which represents whether or not the given $param0T is associated with any Recipient in the $compN (whether or not the Recipient with given e-mail address is registered for his/her Personal Document Store)."),
        # DeliverDocument
        O("deliverDocument",
          ifs["DeliverDocument"],
          "void",
          ["Metadata","Document","Boolean"],
          None,
          "The $compN will ensure the delivery of the $param1T $param1N to the receiver specified in $param0N. $specification",
          [],
          {"DeliveryServiceFacade": {"specification": "The Document will be delivered, either to the Personal Document Store if the document's associated metadata specifies that the document should be delivered by e-mail and the Recipient has a Personal Document Store account, or by one of the 3rd party delivery services (Zoomit, e-mail and postal)."}
          ,"DeliveryHandler":  {"specification": "The Document will be passed on to the appropriate component depending on the required delivery method specified in the associated metadata (\\comp{ZoomitDeliveryHandler}, \\comp{PostalDeliveryHandler} or \\comp{EMailDeliveryHandler})."}
          ,"ZoomitDeliveryHandler": {"specification": "The document will be delivered to Zoomit via their 3rd party API to the Recipient specified in the associated metadata."}
          ,"PostalDeliveryHandler": {"specification": "The document will be delivered to a print and postal service via their 3rd party API to the Recipient specified in the associated metadata. The print quality and other printing related requirements relevant to the print and postal service are specified in the Customer Organization's SLA."}
          ,"EMailDeliveryHandler": {"specification": "The document will be delivered to an e-mail delivery service via their 3rd party API. If the Customer Organization has enabled receipt tracking the e-mail will contain a unique link through which the document can be accessed. The access method depends on the Recipient: if the Recipient specified in the associated metadata does not have a Personal Document Store account the link points to a download location for the document's PDF. If the " +
              " Recipient does have a PDS account the link points to the overview page of that document in their Personal Document Store. The unique links allow eDocs to track when a Recipient accesses their document. If receipt tracking is not enabled the document is sent in the e-mail itself for Unregistered Recipients."}}).changeParamName("Boolean","enableReceiptTracking"),
        # DeliveryCacheMgmt
        O("storeDocument",
          ifs["DeliveryCacheMgmt"],
          "void",
          ["Metadata","Document"],
          None,
          "The $compN will store the given $param1T, along with its $param0T."),
        O("flushDocument",
          ifs["DeliveryCacheMgmt"],
          TupleT(["Metadata","Document"]),
          ["DocumentID"],
          ["DocumentNotFoundException"],
          "The $compN will return the document and its metadata associated with the given $param0T. After this tuple is returned, the document and metadata are deleted from the $compN.",
          ["Thrown if the document that corresponds to the provided $param0T is not found in the cache."]),
        # DeliverNotification
        O("deliverEMailNotification",
          ifs["DeliverNotification"],
          "void",
          ["Notification","Credentials"],
          None,
          "Deliver a $param0T $param0N by E-Mail to a Customer Administrator with $param1T $param1N. (One of the credentials is an e-mail address)"),
        # NotifyDelivery
        O("notifyDelivery",
          ifs["NotifyDelivery"],
          "void",
          ["DocumentID"],
          None,
          "Zoomit calls this operation to indicate that the document with $param0T $param0N has been presented to the intended recipient. The document's Document Status is changed to reflect this successful delivery."),
        # NotifyFailure
        O("notifyFailure",
          ifs["NotifyFailure"],
          "void",
          ["DocumentID"],
          None,
          "The E-Mail Provider calls this operation to indicate that the document with $param0T $param0N could not be delivered to the intended recipient. The document's Document Status is changed to reflect this failed delivery."),
        # InsertJobs
        O("insertJobs",
          ifs["InsertJobs"],
          "void",
          ["BatchID","TimeStamp",ListT("JobID")],
          None,
          "New document generation jobs with Job IDs $param2N get added to the ${compN}'s queue to be scheduled for execution by a \\comp{Generator}."),
        # GetStatistics
        O("getStatistics",
          ifs["GetStatistics"],
          "Statistics",
          [],
          None,
          "The $compN returns $returnT about the near future of required document generation capacity so the \\comp{GeneratorManager} can start up or shutdown \\comp{Generator} instances as required."),
        # GetNextJobs
        O("getNextJobs",
          ifs["GetNextJobs"],
          TupleT(["BatchID",ListT("JobID")]),
          [],
          None,
          "Request a new batch of document generation jobs from the $compN. This method blocks until a new batch of jobs is available."),
        O("jobsCompletedAndGiveMeMore",
          ifs["GetNextJobs"],
          TupleT(["BatchID",ListT("JobID")]),
          [ListT("JobID")],
          None,
          "Request a new batch of document generation jobs from the $compN and report that the previous jobs $param0N have been completed. This method blocks until a new batch of jobs is available."),
        # NotifyCompleted
        O("notifyCompletedAndGiveMeMore",
          ifs["NotifyCompleted"],
          "JobBatch",
          ["GeneratorID"],
          None,
          "Notify the $compN that the Generator identified by $param0T $param0N has completed its most recently assigned generation job and is ready for more."),
        O("notifyCompletedAndIAmShuttingDown",
          ifs["NotifyCompleted"],
          "void",
          ["GeneratorID"],
          None,
          "Notify the $compN that the Generator identified by $param0T $param0N has completed its most recently assigned generation job and is shutting down."),
        # GetTemplate
        O("getTemplate",
          ifs["GetTemplate"],
          "Template",
          ["CustomerID","DocumentType"],
          ["NoSuchTemplateException"],
          "The $compN returns the $returnT used to generate documents of $param1T $param1N for the Customer Organization with $param0T $param0N.",
          ["Thrown if the Customer Organization with the given $param0T doesn't have a $returnT for $param0N."]),
        # GetKey
        O("getKey",
          ifs["GetKey"],
          "DocumentKey",
          ["CustomerID"],
          None,
          "The $compN returns the $returnT used to sign documents for the Customer Organization with $param0T $param0N."),
        # Complete
        O("getComplete",
          ifs["Complete"],
          TupleT([ListT(TupleT(["JobID","RawData"])),"CustomerID","DocumentType","TimeStamp","DocumentKey","Template"]),
          ["BatchID",ListT("JobID")],
          None,
          "The $compN returns all data that are required for the generation of documents for the Raw Data Batch with $param0T $param0N and the specific Job IDs $param1N."),
        # AssignJobs
        O("assignJobs",
          ifs["AssignJobs"],
          "void",
          [ListT("JobID"),ListT("RawData"),"CustomerID","DocumentType","TimeStamp","DocumentKey","Template"],
          None,
          "Assign the document processing jobs identified by $param0N with Raw Data contained in $param1N of $param3T $param3N sent in by the Customer Organization with ID $param2N on $param4N to be generated by the $compN according to $param6T $param6N. When it's generated the resulting document will be signed with $param5T $param5N."),
        # Startup/Shutdown
        O("startup",
          ifs["Startup/Shutdown"],
          "void",
          ["GeneratorID"],
          None,
          "The $compN is started up and when it's ready will be available to get document processing jobs assigned to it."),
        O("shutdown",
          ifs["Startup/Shutdown"],
          "void",
          [],
          None,
          "The $compN is instructed to shut down as soon as possible. If it is still processing jobs it finishes those first and then calls \\texttt{notifyCompletedAndIAmShuttingDown}"),
        # NotifyOperator, NotifyCustomerAdmin, NotifyEDocsAdmin
        O("notifyCustomerAdmin",
          [ifs["NotifyOperator"],ifs["NotifyCustomerAdmin"]],
          "void",
          ["CustomerID","DocumentType","Notification"],
          None,
          "Notify a Customer Organization administrator that something has happened. The relevant Customer Admin for the given document type (that is: the administrator responsible for the department at the company with $param0T $param0N that requires documents of type $param1N to be generated) will receive $param2T $param2N."),
        O("notifyEDocsOperator",
          [ifs["NotifyOperator"],ifs["NotifyEDocsAdmin"]],
          "void",
          ["Notification"],
          None,
          "Notify any eDocs operator that something has happened. The $param0T will be delivered at an eDocs operator's client machine."),
        # RawDataMgmt
        O("addRawDataBatch",
          ifs["RawDataMgmt"],
          "void",
          ["CustomerID","BatchType","BatchID",ListT(TupleT(["Metadata","RawData"])),"TimeStamp"],
          None,
          "The Data Batch $param3N is passed to the $compN to be ${action}.",
          [],
          {"DocumentGenerationHandler":{"action":"processed as a document generation job"}
              ,"PDSDB":{"action":"stored in the PDSDB"}
              ,"PDSReplicationManager":{"action":"stored in the \\comp{PDSDBReplica}"}
              ,"PDSDBReplica":{"action":"stored in the \\comp{PDSDBReplica}"}}),
        # SendDataBatch
        O("sendDataBatch",
          ifs["SendDataBatch"],
          "void",
          ["RawDataCredentials",ListT(TupleT(["Metadata","RawData"]))],
          ["AuthenticationException","InvalidDataException"],
          "$effect",
          ["If the provided $param0T are invalid an $except0T is thrown.","If any of the Raw Data or Metadata is syntactically incorrect or in an incorrect format the \\comp{RawDataFacade} throws an $except1T which is then passed on to the Customer Administrator using the Management Dashboard through the $compN."],
          additionalInfo={
              "RawDataFacade":{"effect":"Use the \\comp{RawDataFacade} to send in a new Raw Data Batch. The syntax of the files that are sent in is checked and an exception is thrown if it is incorrect."},
              "DashboardFacade":{"effect":"It is possible to use the Management Dashboard to send in a new Raw Data Batch. The Batch is then passed to the \\comp{RawDataFacade} which checks the data format for errors."}}),
        # RawDataCommunication
        O("addRawDataCredentials",
          ifs["RawDataCommunication"],
          "void",
          ["RawDataCredentials","CustomerID"],
          None,
          "Add the credentials that the Customer Organization with ID $param1N will use to send in Raw Data Batches to the $compN."),
        O("sendDataBatch",
          ifs["RawDataCommunication"],
          "void",
          ["CustomerID",ListT(TupleT(["Metadata","RawData"]))],
          ["InvalidDataException"],
          "It is possible to use the Management Dashboard to send in a new Raw Data Batch. The Batch is then passed to the $compN which checks the data format for errors.",
          ["If any of the Raw Data or Metadata is syntactically incorrect or in an incorrect format the $compN throws an $except0T which is then passed on to the Customer Administrator using the Management Dashboard through the \\comp{ManagementDashboard}."]),
        # KeyMgmt
        O("addKey",
          ifs["KeyMgmt"],
          "void",
          ["CustomerID","DocumentKey"],
          None,
          "Add a new document signing key to the $compN."),
        # TemplateMgmt
        O("addTemplate",
          ifs["TemplateMgmt"],
          "void",
          ["CustomerID","DocumentType","Template","TimeStamp"],
          None,
          "Change the Customer Organization with $param0T $param0N's current $param2T for $param1T $param1N to $param2N. If there was already a $param2T for $param1N then the old one is kept with the $param3T on which the new $param2T was sent in so it can be used for all document processing jobs that are currently in the queue and were sent in before $param3N."),
        # GetBatchData
        O("getRawData",
          ifs["GetBatchData"],
          ListT(TupleT(["JobID","RawData"])),
          [ListT("JobID")],
          None,
          "Retrieve new Raw Data for the given $param0N."),
        O("getMetaData",
          ifs["GetBatchData"],
          TupleT(["CustomerID","DocumentType","TimeStamp"]),
          ["BatchID"],
          None,
          "Retrieve the Batch metadata for the given $param0N."),
        # FinalizeDocument
        O("storeAndDeliverDocument",
          ifs["FinalizeDocument"],
          "void",
          ["JobID","Document"],
          None,
          "Pass the generated $param1T $param1N back to the $compN to be stored and delivered. The $compN will query the \\comp{CustomerFacade} to see if the Customer Organization that requested ${param1N}'s generation has receipt tracking enabled in order to pass this information to the \\comp{DeliveryServiceFacade}."),
        O("generationError",
          ifs["FinalizeDocument"],
          "void",
          ["JobID","Error"],
          None,
          "Indicate to the $compN that there was an error during the generation process, specified by $param1N"),
        # DocumentCacheMgmt, DocumentMgmt, ExtendedDocumentMgmt
        O("storeDocument",
          [ifs["DocumentCacheMgmt"],ifs["DocumentMgmt"],ifs["ExtendedDocumentMgmt"]],
          "void",
          ["DocumentID","Document","Metadata"],
          None,
          "Store the $param1T $param1N with $param0T $param0N in the $compN with its associated $param2T."),
        O("getDocument",
          [ifs["DocumentCacheMgmt"],ifs["DocumentMgmt"],ifs["ExtendedDocumentMgmt"]],
          TupleT(["Document","Metadata"]),
          ["DocumentID"],
          None,
          "The document with $param0T $param0N is returned from the $compN together with its associated Metadata."),
        O("markReceived",
          ifs["DocumentMgmt"],
          "void",
          ["DocumentID"],
          None,
          "Mark the document with $param0T $param0N as received so it can be moved to the appropriate PDS Database."),
        O("removeDocument",
          ifs["ExtendedDocumentMgmt"],
          TupleT(["Document","Metadata"]),
          ["DocumentID"],
          None,
          "Remove the document with $param0T $param0N from a \\comp{PDSDBReplica} on the \\node{PDSDBReplicaNotDeliveredNode} so that it can be moved to a \\comp{PDSDBReplica} from the \\node{PDSDBReplicaDeliveredNode}."),
        # GenerateUniqueLink
        O("generateUniqueLink",
          ifs["GenerateUniqueLink"],
          "UniqueDocumentToken",
          ["DocumentID"],
          None,
          "Generate a $returnT that can be embedded in a URL to retrieve the document with $param0T $param0N for which receipt tracking has been enabled.")
    ]

ops = { op.getName():op for op in operations }

ops["insertJobs"].changeParamName("TimeStamp","deadline")
ops["getComplete"].changeParamName("TimeStamp","whenReceived")
ops["consultNumberOfStatuses"].changeParamName("Integer","number")
ops["addRawDataBatch"].changeParamName("TimeStamp","whenReceived")

### REFACTORING (werkt niet!) ###

def refactor(theType="", oldName="", newName=""):
    if theType and oldName and newName:
        refactors[theType][oldName] = newName
    else:
        ops = {"CO": C.refactor
              ,"IF": C.refactorIF
              ,"OP": C.refactorOp
              ,"DT": C.refactorDT
              ,"EX": C.refactorEx}
        for t in refactors:
            comps = list(map(lambda c: cs[c], refactors[t]))
            for comp in comps:
                for old in refactors[t]:
                    ops[t](comp,old,refactors[t][old])
def refactored(oldName):
    allNames = {name: t for (t,sub) in refactors.items() for name in sub}
    if oldName in allNames:
        return refactors[allNames[oldName]][oldName]
    else:
        return oldName

### DATA TYPES ###

#allTypes = {t for comp in components for t in comp.getSubtypes()}

### EXECUTION ###

refactor()
for comp in sorted(components, key=C.getName):
    print(comp)
#print("\n".join(sorted(map(str,allTypes))))
