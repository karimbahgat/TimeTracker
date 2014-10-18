import Tkinter as tk
import datetime
import pickle
import sys, os

# Note: Because this package relies on read/writing logfiles in the same directory as the package itself
# it cannot be bundled in a zipfile when using it in an app, it must be included as an
# regular folder (ie the "includes" arg instead of the "packages" arg)
PACKAGE_DIR = None
for syspath in sys.path:
    if os.path.lexists(syspath):
        if os.path.isdir(syspath): # in case it runs across a zipfile (in the case of bundled apps where dependencies are accessed via a zipfile)
            for checkpath in os.listdir(syspath):
                checkpath = os.path.join(syspath,checkpath)
                if checkpath.endswith("timetracker"):
                    PACKAGE_DIR = checkpath
                    break
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
        from . import app
        app.run()

    # run the tests
    # test_IDLE()
    test_GUI()
    print "tests finished"
    
