import Tkinter as tk
import datetime
import pickle
import sys, os

PACKAGE_DIR = None
for syspath in sys.path:
    if os.path.lexists(syspath):
        for checkpath in os.listdir(syspath):
            checkpath = os.path.join(syspath,checkpath)
            if checkpath.endswith("timetracker"):
                PACKAGE_DIR = checkpath
if not PACKAGE_DIR: raise Exception("The timetracker package is not in a valid sys.path location, which it needs in order to find and save timelogs within the timetracker folder structure")

DEFAULT_MEMORYFILE = os.path.join(PACKAGE_DIR, "default_activitylog.pkl")

################
### CLASSES ###
################

class Activity:
    """
    An activity that is started, can be paused, and stopped
    """
    def __init__(self, category, details=None):
        self.category = category
        self.details = details
        self.started = datetime.datetime.now()
        self.stopped = None

    def stop(self):
        self.stopped = datetime.datetime.now()
        self.duration = self.stopped - self.started

class Logger:
    """
    The one that keeps track of, writes, and retrieves activity records in a logfile.
    """
    def __init__(self, memorypath):
        """
        - memorypath: this is used as the location to an existing logfile.
        """
        self.memorypath = memorypath                
        self.current = None

    def __iter__(self):
        for act in self.activities:
            yield act

    @property
    def activities(self):
        memorybox = open(self.memorypath, "rb")
        activities = pickle.load(memorybox)
        memorybox.close()
        # validate the pickle
        if not activities: activities = []
        elif not isinstance(activities, list): activities = list(activities)
        return activities
    
    def start(self, category, **kwargs):
        """Start a new activity"""
        self.current = Activity(category, **kwargs)

    def stop(self):
        """Stop the current activity"""
        self.current.stop()
        self.__log_current__()
        self.current = None

    def reset(self):
        memorybox = open(self.memorypath, "wb")
        pickle.dump([], memorybox)
        memorybox.close()

    # Internal use only

    def __log_current__(self):
        # get current info
        curinfo = dict()
        for key, value in self.current.__dict__.items():
            if not key.startswith("__"):
                curinfo.update([(key,value)])
        # append it to existing
        activities = self.activities
        activities.append(curinfo)
        # save to pickle
        memorybox = open(self.memorypath, "wb")
        pickle.dump(activities, memorybox)
        memorybox.close()

class LogfileManager:
    """
    Remembers all logfiles that have been created, and can edit or add new ones.
    """
    def __init__(self):
        self.managermemory = PACKAGE_DIR+"/registry.pkl"

    @property
    def files(self):
        if not os.path.lexists(self.managermemory):
            # restore manager file if somehow deleted
            restorefile = open(self.managermemory, "wb")
            pickle.dump(dict(), restorefile)
            restorefile.close()
        memorybox = open(self.managermemory, "rb")
        logfiles = pickle.load(memorybox)
        memorybox.close()
        return logfiles

    def addfile(self, name, filepath):
        # error checking
        if self.files.get(name): 
            raise Exception("There is already an existing file with that name identifier")
        if os.path.lexists(filepath):
            raise Exception("There is already an existing file in the path where you are attempting to create a new logfile")
        # create the actual logfile
        memorybox = open(filepath, "wb")
        pickle.dump([], memorybox)
        memorybox.close()
        # register the new logfile with the manager
        logfiles = self.files
        logfiles.update([( name, dict([("filepath",filepath)]) )])
        memorybox = open(self.managermemory, "wb")
        pickle.dump(logfiles, memorybox)
        memorybox.close()

    def getfile(self, name):
        # get the memoryfile if it exists
        getinfo = self.files.get(name)
        if not getinfo:      
            raise Exception("There is no registered file with that name identifier")
        if not os.path.lexists(getinfo["filepath"]):
            # delete the entry for that name since the filepath no longer exists
            logfiles = self.files
            del logfiles[name]
            memorybox = open(self.managermemory, "wb")
            pickle.dump(logfiles, memorybox)
            memorybox.close()
            raise Exception("The logfile at the path of the given name no longer exists, the name is now unregistered.")
        return Logger(getinfo["filepath"])

    def deletefile(self, name):
        # first delete registry entry
        getinfo = self.files.get(name)
        if not getinfo:
            raise Exception("There is no registered file with that name identifier")
        logfiles = self.files
        del logfiles[name]
        memorybox = open(self.managermemory, "wb")
        pickle.dump(logfiles, memorybox)
        memorybox.close()
        # then delete file
        if os.path.lexists(getinfo["filepath"]):
            os.remove(getinfo["filepath"])





################
### FUNCTIONS
################

def newfile(name, filepath=None):
    """
    - name: unique name of the logfile one wants to create.
    - filepath: this is used as the location for the file (if omitted save it in the package directory). The user does not have to worry about remembering the locations of the files, only their names. 
    """
    # create a new logfile at the specified path (if omitted save it in the package directory)
    if not filepath: filepath = PACKAGE_DIR+"/"+str(name)+"_logfile.pkl"
    manager = LogfileManager()
    manager.addfile(name, filepath)
    return manager.getfile(name)

def loadfile(name):
    """
    - name: unique name of the logfile one wants to load.
    """
    manager = LogfileManager()
    return manager.getfile(name)

def deletefile(name):
    manager = LogfileManager()
    return manager.deletefile(name)

def files():
    manager = LogfileManager()
    return manager.files




        
################
### THE GUI ###
################
    
def create_GUI():
    window = tk.Tk()

    # misc
    appfont = "calibri"
    gray = "Gray18"
    goodcolor = (80, 222, 110)
    badcolor = (222, 0, 0)
    moodcolor = tuple(goodcolor)
    def transition(value, maximum, start_point, end_point):
        return start_point + (end_point - start_point)*value/float(maximum)
    def transition3(value, maximum, (s1, s2, s3), (e1, e2, e3)):
        r1= transition(value, maximum, s1, e1)
        r2= transition(value, maximum, s2, e2)
        r3= transition(value, maximum, s3, e3)
        return (r1, r2, r3)

    # top file choices
    filesframe = tk.Frame(window, bg=gray)
    filesframe.pack(side="top", fill="both")
    def choosefile(event, name):
        global logger
        logger = loadfile(name)
        for filebut in filebuts:
            if filebut["text"] == name:
                filebut["bg"] = "light blue"
                filebut["relief"] = "sunken"
            else:
                filebut["bg"] = "light gray"
                filebut["relief"] = "groove"
        nameentry["state"] = "normal"
        actbut["state"] = "normal"
        viewbut["state"] = "normal"
        timebut["state"] = "normal"
    def deleteoldfile(event, name):
        deletefile(name)
        updatefilebuts()
    def viewfileoptions(event,name):
        deletebut = tk.Label(window, text="Delete file", relief="groove", bg="orange")
        deletebut.bind("<Button-1>", lambda event,name=name: deleteoldfile(event,name) )
        deletebut.place(x=event.x, y=event.y)
    def updatefilebuts():
        for filebut in filebuts:
            filebut.destroy()
        filebuts[:] = []
        for name in files().keys():
            namebut = tk.Label(filesframe, text=name, font=appfont, relief="groove", bg="light gray")
            filebuts.append(namebut)
            namebut.bind("<Button-1>", lambda event,name=name: choosefile(event,name) )
            namebut.bind("<Button-2>", lambda event,name=name: viewfileoptions(event,name) )
            namebut.pack(side="left")
    filebuts = []
    updatefilebuts()

    # create new file
    def createnewfile(name):
        newfile(name)
        updatefilebuts()
        newfileentry.delete(0, tk.END)
    newfileframe = tk.Frame(window, bg=gray)
    newfileframe.pack(side="top", fill="both")
    newfileentry = tk.Entry(newfileframe, font=appfont)
    newfileentry.grid(row=0, column=0)
    newfilebut = tk.Button(newfileframe, text="Create New Log", font=appfont,
                           command=lambda: createnewfile(newfileentry.get()) )
    newfilebut.grid(row=0, column=1)
    
    # timer clock
    countlength = datetime.timedelta(hours=0,minutes=25,seconds=0)
    global countdown
    countdown = datetime.timedelta(seconds=countlength.seconds)
    clockframe = tk.Frame(window)
    clockframe.pack(side="top", fill="both")
    def updateclock():
        global countdown
        if actbut.running and countdown > datetime.timedelta(seconds=0):
            countdown -= datetime.timedelta(seconds=1)
        hours = countdown.seconds/60/60
        minutes = countdown.seconds/60 - hours*60
        seconds = countdown.seconds - minutes*60 - hours*60
        clock["text"] = "%02d:%02d:%02d"%(hours,minutes,seconds)
        clock["bg"] = "#%02x%02x%02x"%transition3(countdown.seconds, countlength.seconds, badcolor, goodcolor)
        window.after(1000, updateclock)
    clock = tk.Label(clockframe, bg="#%02x%02x%02x"%moodcolor, height=2,
                     font=appfont+' 65 bold', fg="Gray18")
    clock.pack(fill="both")
    window.after(1, updateclock)
    
    # set up buttons
    buttonframe = tk.Frame(window, bg=gray)
    buttonframe.pack(side="bottom", fill="both")
    
    nameentry = tk.Entry(buttonframe, font=appfont)
    nameentry.grid(row=0,column=0, columnspan=2)

    def toggle_act(name):
        if actbut.running: stop_act()
        else: new_act(name)
        actbut.running = not actbut.running
    
    def new_act(name):
        actbut["text"] = "Stop Activity"
        logger.start(name)
        nameentry["state"] = tk.DISABLED
        global countdown
        countdown = datetime.timedelta(seconds=countlength.seconds)
        moodcolor = tuple(goodcolor)

    def stop_act():
        actbut["text"] = "New Activity"
        logger.stop()
        nameentry["state"] = tk.NORMAL
        nameentry.delete(0, tk.END)

    global actbut
    actbut = tk.Button(buttonframe, text="New Activity", font=appfont, command=lambda: toggle_act(nameentry.get()) )
    actbut.running = False
    actbut.grid(row=0,column=2)
    
    def view_acts():
        for act in logger:
            print "---"
            print str(act)
    viewbut = tk.Button(buttonframe, text="View All", font=appfont, command=view_acts)
    viewbut.grid(row=1,column=2)#, columnspan=3)
    
    def totaltime():
        durations = (act["duration"] for act in logger)
        print sum(durations, datetime.timedelta() )
    timebut = tk.Button(buttonframe, text="Calculate Time", font=appfont, command=totaltime)
    timebut.grid(row=2,column=2)#, columnspan=3)

    actbut["state"] = "disabled"
    viewbut["state"] = "disabled"
    timebut["state"] = "disabled"

    #TEMP
    #listbox = tk.OptionMenu(buttonframe, "one", "two", "three")
    #listbox.grid()
    
    # run
    window.attributes("-topmost", True)
    window.mainloop()





################
### TEST RUN ###
################
    
if __name__ == "__main__":

    def test_IDLE():
        import time
        # setup
        logger = newfile("testlog")
        # first
        logger.start("waiting for worklog test")
        time.sleep(1)
        logger.stop()
        # second
        logger.start("numero deus")
        time.sleep(1)
        logger.stop()
        # retrieve
        for act in logger:
            print "----"
            print act
        # maybe delete after test
        deletefile("testlog")

    def test_GUI():
        create_GUI()

    # run the tests
    # test_IDLE()
    test_GUI()
    print "tests finished"
    
