################
### THE GUI ###
################

from . import main
from main import *

def run():
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
