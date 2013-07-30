"""
Observer pattern module used for managing object communications
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

A Subscriber subscribes to an Observer.
A Subscriber can also publish to their Observer.
An Observer can publish to each Subscriber that has subscribed with it.

Publish here means to send messages to all Subscriber objects to do something, as in call
one of their methods with options.

The Observer plays the role of an Interaction manager. 
Observer manages individual messages on the receving end to compare against
the set of interactions it manages to determine which subscribers should respond to the
message and how they should respond.

New interactions can be defined to be managed by the Observer.
"""




class Subscriber:
    """
    Controls communication between a subject and and observer.
    """
    def __init__(self,observer):
        """
        observer (Observer): who the subsriber subscribes to.
        """
        self.buildMethods()
        self.observer.subscribe(self)

    def dispatch(self,commandName,options=[]):
        """
        Calls commandName method of encapsulating object. Provides runtime
        access to methods of an object.

        commandName (string):  Name of method of encapsulating object to call.

        options (list):  options for method.
        """
        if options:
            self.methods[commandName](options)
        else:
            self.methods[commandName]()

    def publish(self,commandName,options=[]):
        """
        Notify observer that subject is executing a method.

        commandName (string): method object is executing.
        options (list): options used with method.
        """
        self.observer.processSignal(self.name,self.type,commandName,options)

    def buildMethods(self):
        """
        Initializes dictionary holding methods that will be made public to
        Observer.
        """
        self.methods = {}

    def addMethod(self,methodName,method):
        """
        Add a method to the dictionary holding methods I want to be public to
        my Observer.

        methodName (string): name of method to make public to Observer
        method (function-method): the method itself
        """
        self.methods[methodName] = method

    def unsubscribe(self):
        """
        Remove me from the Observer's list of subscribers.
        """
        self.observer.unsubscribe(self)

class Interaction:
    """
    View to view interaction. Defines an association between a sending Class
    and a receiving Class.
    """

    def __init__(self, mode, senderType, senderCommand, responderType,
                 responderCommand):
        """
        Constructor to build an interaction.

        mode (string): interaction name.
        senderType (string): type of object origining the interaction.
        senderCommand (string): name of method sending object has executed.
        responderType (string): type of object that should respond to this
            interaction.
        responderCommand (string): name of method responders should call to
            complete interaction.
        """

        self.mode = mode
        self.senderType = senderType
        self.senderCommand = senderCommand
        self.responderType = responderType
        self.responderCommand = responderCommand
        self.key = mode+senderType+senderCommand+responderType+ \
                   responderCommand
        self.originKey = mode+senderType+senderCommand

    def summary(self):
        """
        provides a print listing of attributes for the interaction.
        """
        print "Interaction key: %s"%(self.key)
        print "Sender Type: %s"%self.senderType
        print "Sender Command: %s"%self.senderCommand
        print "Responder Type: %s"%self.responderType
        print "Responder Command: %s"%self.responderCommand

class Interactions:
    """
    Container for all Interaction instances.
    """

    def __init__(self):
        self.modes = {}
        self.interactions={}
        self.origins = {}

    def addInteraction(self, mode, senderType, senderCommand, responderType,
                       responderCommand):
        """
        Adds a new interaction to the list of interactions.

        mode (string): interaction mode.
        senderType (string): type of sending object
        senderCommand (string): method sending object will have executed and
            wants the world to respond to.
        responderType (string): type of object that should respond.
        responderCommand (string): method that responding object should call
            to complete interaction.
        """
        interaction = Interaction(mode, senderType, senderCommand,
                      responderType, responderCommand)
        self.interactions[interaction.key] = interaction
        if self.modes.has_key(interaction.mode):
            self.modes[interaction.mode].append(interaction.key)
        else:
            self.modes[interaction.mode] = [interaction.key]

        if self.origins.has_key(interaction.originKey):
            self.origins[interaction.originKey].append(interaction)
        else:
            self.origins[interaction.originKey]=[interaction]

    def getInteractions(self,mode):
        """
        Accessor for all interactions associated with a given type of
        interaction mode.

        mode (string): name of interaction mode.

        Returns (list) of (strings) with interaction names associated with
            this mode.
        """
        return self.modes[mode]

    def getOrigins(self,originKey):
        """
        Get all interactions associated with a specific origin signal.

        originKey (string): concatenated string with senderType and
            senderCommand as the origin signal
        """
        if self.origins.has_key(originKey):
            return self.origins[originKey]

    def listInteractions(self):
        """
        Prints all interactions that belong to this object.
        """
        for key in self.interactions.keys():
            self.interactions[key].summary()

class Observer:
    """
    Watcher class. Receives messages from Subscribers and sends messages to
    Subscribers. Many-to-one on receiving end, one-to-many on the sending end.
    """
    def __init__(self):
        self.items={}
        self.types = {}
        self.__interActionMode="off"
        self.interactions=Interactions()

    def subscribe(self,item):
        """
        Add an item to the Observers list of Subscribers.

        item (Subscriber): 
        """
        self.items[item]=item
        itype = item.type
        if self.types.has_key(itype):
            self.types[itype].append(item)
        else:
            self.types[itype]=[item]

    def unsubscribe(self,item):
        """
        Remove an item from list of Subscribers.

        item (Subscriber):
        """
        itype = item.type
        if self.items.has_key(item):
            del self.items[item]
            self.types[itype].remove(item)

    def listItems(self):
        """
        Print out a list of subscribers by subscriber types.
        """
        for item in self.items.keys():
            print self.items[item]
        for typeKey in self.types.keys():
            print typeKey
            for item in self.types[typeKey]:
                print item,typeKey

    def setInteractionMode(self,interActionMode):
        """
        Set interactionMode that is used for determining how publishing should
        be done.

        interactionMode (string): name of interaction mode.
        """
        self.__interActionMode = interActionMode

    def getInteractionMode(self):
        """
        accessor for interactionMode.

        returns interactionMode (string)
        """
        return self.__interActionMode
        
    def addInteraction(self, mode, senderType, senderCommand, responderType,
                       responderCommand):
        """
        Adds a new interaction to list of interactions that Observer can
        process and use in publishing.

        mode (string): name of interaction mode.
        senderType (string): type of object sending the message to Observer.
        senderCommand (string): name of method that the sender has published.
        responderType (string): type of objects that can respond to this
            interaction.
        responderCommand (string): name of responder method that should be
            executed in response to this message.
        """
        self.interactions.addInteraction(mode, senderType, senderCommand,
                                         responderType, responderCommand)

    def listInteractions(self,full=[]):
        """
        Prints out a list of interactions the Observer manages.
        """
        keys=self.interactions.interactions.keys()
        print "there are %d interactions defined"%len(keys)
        if full:
            self.interactions.listInteractions()

    def processSignal(self,senderName,senderType,commandName,options=[]):
        """
        Determines which subscribers need to be notified about the message
        received from senderName.

        senderName (string): object sending the message
        sendterType (string): class of sending object
        commandName (string): name of method that the sending object has
            executed.
        options (list): list of options used with executed method.
        """
        publishKey=senderType+commandName
        mode = self.getInteractionMode()
        #print "publishkey",publishKey
        if mode:
            #print senderName
            key = mode+publishKey
            interactions = self.interactions.getOrigins(key)
            if interactions:
                for interaction in interactions:
                    responderType = interaction.responderType
                    command = interaction.responderCommand
                    #print "responderType",responderType
                    #print "command",command
                    if self.types.has_key(responderType):
                        responders = self.types[responderType]
                        #print "responders",responders
                        for responder in responders:
                            #print "responder type",responder.type
                            #print "command before if",command
                            #print "responder.name",responder.name
                            if responder.name != senderName:
                            #    print "command",command
                                responder.dispatch(command,options)

if __name__ == '__main__':

    # this is an illustrative example of how to use the classes above to
    # manage view-view interactions. all the classes below here will be
    # defined in other modules (such as View.py)

    from iview import IMap,IScatter,IHistogram,ITimeSeries
    from numpy.oldnumeric import *

    class Scatter(Subscriber):
        nscatter = 0
        """ """

        def __init__(self,observer, variableX,valuesX, variableY,valuesY, t):
            self.matcher=IScatter(variableX,valuesX, variableY,valuesY,t)
            self.observer=observer
            self.type="scatter"
            Scatter.nscatter +=1
            self.name="scatter_%d"%Scatter.nscatter
            Subscriber.__init__(self,observer)

        def selectPoints(self,pointIds):
            print self.name," will select points",pointIds

        def selectedPoints(self,pointIds):
            print self.name,"selected point",pointIds

        def brushPoints(self,pointIds):
            print self.name," will brush on points",pointIds

        def selectObservations(self,observations):
            print self.name, "will select ids associated with observations"
            ids = self.matcher.matchObservations(observations)
            self.selectPoints(ids)

        def selectedObservations(self,observations):
            #self.dispatch("selectObservations",observations)
            self.selectObservations(observations)
            #print "snd"
            self.publish("selectedObservations",observations)

            #self.selectObservations(observations)

        def updateTime(self,tsId):
            tsid = tsId[0].ts
            print self.name," is updating to time period",tsid

        def buildMethods(self):
            m={}
            m={"selectPoints":self.selectPoints,
               "selectedPoints":self.selectedPoints,
               "brushPoints":self.brushPoints,
               "selectObservations":self.selectObservations,
               "selectedObservations":self.selectedObservations,
               "updateTime":self.updateTime}
            self.methods=m

    class Map(Subscriber):
        nmap=0
        def __init__(self,observer,varName,variable,t,poly2cs,cs2poly):
            self.matcher = IMap(varName,variable,t,poly2cs,cs2poly)
            #print self.matcher.cs2poly
            self.observer=observer
            self.type="map"
            Map.nmap +=1
            self.name = "map_%d"%Map.nmap
            Subscriber.__init__(self,observer)
            self.addMethod("testMethod",self.testMethod)

        def selectPolygons(self,polyIds):
            #rint self.name," will select polygons ",polyIds
            self.matcher.select(polyIds)

        def selectedPolygons(self,polyIds):
            #rint self.name," selected polygons",polyIds
            self.matcher.select(polyIds)
        
        def brushPolygons(self,polygonIds):
            print self.name," will brush on polygons",polygonIds

        def selectObservations(self,observations):
            ids = self.matcher.matchObservations(observations)
            #print ids
            self.selectPolygons(ids)

        def selectedObservations(self,observations):
            self.selectObservations(observations)
            self.publish("selectedObservations",observations)
            
        def buildMethods(self):
            m={}
            m={"selectPolygons":self.selectPolygons,
               "selectedPolygons":self.selectedPolygons,
               "brushPolygons":self.brushPolygons,
               "selectedObservations":self.selectedObservations,
               "selectObservations":self.selectObservations}
            self.methods=m
        def testMethod(self):
            print "Im test method"

    class Histogram(Subscriber):
        nhist = 0
        def __init__(self,observer,variable,values,tsid,csid,binInfo=[] ):
            #self.matcher=IHistogram(variable,values,tsid,csid,binInfo=[])
            self.matcher=IHistogram(variable,values,tsid,csid,bins=binInfo)
            self.observer = observer
            self.type="histogram"
            Histogram.nhist += 1
            self.name = "hist_%d"%Histogram.nhist
            Subscriber.__init__(self,observer)

        def selectIds(self,ids):
            self.matcher.select(ids)

        def selectObservations(self,observations):
            ids = self.matcher.matchObservations(observations)
            self.selectIds(ids)

        def selectBinforIds(self,ids):
            bins=self.matcher.getBinsforIds(ids)
            #print bins


        def buildMethods(self):
            m = {}
            m = {"selectIds":self.selectIds,
                 "selectObservations":self.selectObservations}
            self.methods = m

    class TimeSeries(Subscriber):
        """ """
        nTimeSeries = 0
        def __init__(self,observer,variable,values,tsid,csid ):
            self.matcher=ITimeSeries(variable,values,tsid,csid)
            self.observer = observer
            self.type="timeSeries"
            TimeSeries.nTimeSeries +=1
            self.name = "ts_%d"%TimeSeries.nTimeSeries
            Subscriber.__init__(self,observer)

        def selectIds(self,ids):
            self.matcher.select(ids)

        def selectObservations(self,observations):
            ids = self.matcher.matchObservations(observations)
            self.selectIds(ids)
        def selectedObservations(self,observations):
            ids = self.matcher.matchObservations(observations)
            self.publish("selectedObservations",observations)

        def buildMethods(self):
            m = {"selectObservations":self.selectObservations,
                 "selectedObservations":self.selectedObservations}
            self.methods = m


    # create an observer
    ob=Observer()

    # define types of view-view interactions
    ob.addInteraction("brushing", "map", "selectedPolygons",
                      "scatter", "brushPoints")
    ob.addInteraction("brushing", "scatter", "selectedPoints",
                      "scatter", "brushPoints")
    ob.addInteraction("linking", "map", "selectedPolygons",
                      "scatter", "selectPoints")
    ob.addInteraction("linking", "map", "selectedPolygons",
                      "map", "selectPolygons")
    ob.addInteraction("linking", "scatter", "selectedPoints",
                      "map", "selectPolygons")
    ob.addInteraction("linking", "scatter", "selectedPoints",
                      "scatter", "selectPoints")
    ob.addInteraction("linking", "map", "selectedObservations",
                      "scatter", "selectObservations")
    ob.addInteraction("brushing", "map", "selectedObservations",
                      "scatter", "selectObservations")
    ob.addInteraction("brushing", "scatter", "selectedObservations",
                      "map", "selectObservations")
    ob.addInteraction("brushing", "map", "selectedObservations",
                      "histogram", "selectObservations")
    ob.addInteraction("brushing", "map", "selectedObservations",
                      "timeSeries", "selectObservations")
    ob.addInteraction("brushing", "timeSeries", "selectedObservations",
                      "scatter", "updateTime")
    # make up some fake data 55 polygons 40 observations 10 time periods
    N=40
    T=10

    var1 = reshape(arange(N*T),[N,T])
    timeVar = arange(0,T)
    var2 = var1 * 100
    
    #polys 0-37 match obser 0-37
    #polys 36-45 match obs 38
    #polys 46-54 match obs 39
    cs2poly = {}
    for id in range(38):
        cs2poly[id] = [id]
    cs2poly[38] = range(38,45)
    cs2poly[39] = range(45,55)

    poly2cs={}

    for key in cs2poly.keys():
        ids = cs2poly[key]
        for id in ids:
            poly2cs[id] = [key]

    # create some view instances
    m1 = Map(ob,"var1",var1[:,0],0,poly2cs,cs2poly)
    s1 = Scatter(ob,"var1",var1[:,0],"var2",var2[:,0],0)
    h1 = Histogram(ob,"var1",var1[:,3],tsid=3,csid=range(N))
    t1 = TimeSeries(ob,"var1",var1[0,:],tsid=range(T),csid=[])
    #s2 = Scatter(ob)
    #m2 = Map(ob)

    # using the iview matcher class
    ob.setInteractionMode("brushing")
    
    # with iview classes
    m1.matcher.select(range(37,55))
    mobs = m1.matcher.getSelected()
    print "selected in histogram", h1.matcher.selected
    m1.selectedObservations(mobs)
    print "selected in histogram", h1.matcher.selected
    ob.setInteractionMode("brushing")
    print "after turning off interaction"
    m1.selectedObservations(mobs)
    print "selected in histogram should be off", h1.matcher.selected
    m1.selectedObservations(mobs)
    print "selected in histogram", h1.matcher.selected
