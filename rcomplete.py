import multiprocessing

from subprocess import PIPE, Popen, call
import threading
import Queue
import sys
from os import path, chmod, listdir, environ
from merge import mergeHKLFile
import os

IDLE = False

FNULL = open(os.devnull, 'w')

maxCPU = multiprocessing.cpu_count()
global exitFlag
exitFlag =False
lock = threading.Lock()
msgLock = threading.Lock()

mergeProgress = ''


def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


# def generateReflectionFiles(fileName, setSize):
#     try:
#         make_executable(path.join(sys._MEIPASS,'crossflaghkl'))
#     except AttributeError:
#         call(['crossflaghkl', '-t'+str(setSize), '-r.k', fileName], stdout=FNULL)
#     else:
#         call([path.join(sys._MEIPASS,'crossflaghkl'), '-t'+str(setSize), '-r.k', fileName], stdout=FNULL)


# class Merger(threading.Thread):
#     def __init__(self, insfileName, hklFileName, outFileName, callback):
#         super(Merger, self).__init__()
#         self.ins = insfileName
#         self.hkl = hklFileName
#         self.out = outFileName
#         self.callback = callback
#         updateMergeProgress()
#         self.start()
#
#     def run(self):
#         mergeHKLFile(self.ins, self.hkl, self.out, self.callback)


# def mergeCallback(msg):
#     global mergeProgress
#     mergeProgress = msg
#     # root.after(10, updateMergeProgress)
#
#
# def updateMergeProgress():
#     status['text'] = mergeProgress
#     if mergeProgress == 'Data merged successfully.':
#         _load()
#     else:
#         root.after(100, updateMergeProgress)


def load():
    global IDLE
    if not IDLE:
        return
    IDLE = False
    # global mergeCheck
    # if mergeCheck.get():
    #     # mergeHKLFile(insFile.get(),hklFile.get(),'_merged.hkl',)
    #     # m = Merger(insFile.get(),hklFile.get(),'_merged.hkl', mergeCallback)
    #     # hklFile.set('_merged.hkl')
    #     return
    # else:
    _load()


def _load():
    cmds = ['REM',
            'BEDE',
            'MOLE',
            'TITL',
            'CELL',
            'ZERR',
            'LATT',
            'SYMM',
            'SFAC',
            'UNIT',
            'TEMP',
            'L.S.',
            'BOND',
            'ACTA',
            'LIST',
            'FMAP',
            'PLAN',
            'WGHT',
            'FVAR',
            'SIMU',
            'RIGU',
            'SADI',
            'SAME',
            'DANG',
            'AFIX',
            'PART',
            'HKLF',
            'ABIN',
            'ANIS',
            'ANSC',
            'ANSR',
            'BASF',
            'BIND',
            'BLOC',
            'BUMP',
            'CGLS',
            'CHIV',
            'CONF',
            'CONN',
            'DAMP',
            'DEFS',
            'DELU',
            'DFIX',
            'DISP',
            'EADP',
            'EQIV',
            'EXTI',
            'EXYZ',
            'FEND',
            'FLAT',
            'FMAP',
            'FRAG',
            'FREE',
            'GRID',
            'HFIX',
            'HTAB',
            'ISOR',
            'LATT',
            'LAUE',
            'MERG',
            'MORE',
            'MPLA',
            'NCSY',
            'NEUT',
            'OMIT',
            'PLAN',
            'PRIG',
            'RESI',
            'RTAB',
            'SADI',
            'SAME',
            'SHEL',
            'SIMU',
            'SIZE',
            'SPEC',
            'STIR',
            'SUMP',
            'SWAT',
            'TWIN',
            'TWST',
            'WIGL',
            'WPDB',
            'XNPD',
            'REM',
            'Q',
            'END',
            'BEDE',
            'LONE',
    ]
    with open(hklFile.get(), 'r') as hkl:
        for i, _ in enumerate(hkl.readlines()):
            pass
        i += 1

    nHKL.set(i)
    nHKLLabel['text'] = str(i)

    with open(insFile.get(), 'r') as ins:
        global insContent
        insContent = ins.readlines()
    nAtoms = 0
    for line in insContent:
        if line[0] == ' ':
            continue
        line = [_ for _ in line.split() if _]
        if not line:
            continue
        if not line[0].upper() in cmds and not line[0].upper() == 'Q':
            nAtoms += 1
    nParams.set(nAtoms)
    nParamsLabel['text'] = str(nAtoms)
    nFree.set(int(i*float(fracFree.get())/100.))
    status['text'] = 'Input loaded. Ready to run.'
    percentScale('')
    global IDLE
    IDLE = True


def browseINS():
    from tkFileDialog import askopenfilename
    insFile.set(askopenfilename())
    hklGuess = path.splitext(insFile.get())[0]+'.hkl'
    if path.isfile(hklGuess) and not hklFile.get():
        hklFile.set(hklGuess)


def browseHKL():
    from tkFileDialog import askopenfilename
    hklFile.set(askopenfilename())
    resGuess = path.splitext(hklFile.get())[0]+'.res'
    if insFile.get():
        return
    if path.isfile(resGuess):
        insFile.set(resGuess)

    insGuess = path.splitext(hklFile.get())[0]+'.ins'
    if path.isfile(insGuess):
        insFile.set(insGuess)


def run():
    global IDLE
    if not IDLE:
        return
    IDLE = False
    if not status['text'] == 'Input loaded. Ready to run.' and not 'Done' in status['text']:
        status['text'] = 'Error. No input files loaded.'
        return
    # status['text'] = 'Running. Generating HKL files.'
    try:
        make_executable(path.join(sys._MEIPASS,'shelxl'))
    except:
        pass
    root.after(10, _run)


def _run():
    k = nFree.get()
    # generateReflectionFiles(hklFile.get(), k)
    # status['text'] = 'Working... HKL files generated.'

    global insContent
    foundList = False
    foundMerge = False
    for i, line in enumerate(insContent):
        if line[:4].upper() == 'L.S.' or line[:4].upper() == 'CGLS':
            insContent[i] = '{} {} -1\n'.format('L.S.' if lsType.get() == 2 else 'CGLS',
                                                str(cycles.get()))
        if line[:4].upper() == 'ACTA':
            insContent[i] = ''

        if line[:4].upper() == 'WPDB':
            insContent[i] = ''

        if line[:4].upper() == 'LIST' and compileMap.get():
            insContent[i] = 'LIST 9\n'
            foundList = True

        if line[:4].upper() == 'MERG':
            insContent[i] = 'MERG 4\n'
            foundMerge = True

    if not foundList and compileMap.get():
        for i, line in enumerate(insContent):
            if line[:4].upper() == 'L.S.' or line[:4].upper() == 'CGLS':
                insContent = insContent[:i+1] + ['List 9\n'] + insContent[i+1:]
                break

    if not foundMerge:
        for i, line in enumerate(insContent):
            if line[:4].upper() == 'L.S.' or line[:4].upper() == 'CGLS':
                insContent = insContent[:i+1] + ['MERG 4\n'] + insContent[i+1:]
                break

    insContent = ''.join(insContent)

    global threads
    threads = []
    global exitFlag
    exitFlag =False
    nFiles = int(float(nHKL.get())/float(k))+1
    queue = Queue.Queue(nFiles)
    msgQueue = Queue.Queue(1)
    msgQueue.put(0)
    setStatus('test')
    for n in xrange(nFiles):
        n += 1
        queue.put(('.k_set{:0>4}.hkl'.format(str(n)),n))
    for i in xrange(nCPU.get()):
        t = WorkerThread(i, queue, msgQueue, insContent, hklFile.get(), nHKL.get() / nFree.get())
        threads.append(t)
        t.start()
    i=0
    updater = StatusUpdater(i, msgQueue, nFiles)
    root.after(100, updater)


class StatusUpdater(object):
    def __init__(self, i, msgQueue, nFiles):
        self.i = i
        self.msgQueue = msgQueue
        self.nFiles = nFiles
        self.__name__ = 'StatusUpdater'

    def __call__(self, *args, **kwargs):
        msgLock.acquire()
        msg = self.msgQueue.get()
        self.msgQueue.put(0)
        self.i += msg
        msgLock.release()

        toGo = self.nFiles - self.i
        setStatus('Running. Files remaining: {}'.format(toGo))
        if toGo:
            root.after(100, self)
        else:
            global exitFlag
            exitFlag = True
            setStatus('Done.')
            finish()


def finish():
    ds = []
    for d in [thread.ds for thread in threads]:
        ds += d
    fs = []
    for f in [thread.fs for thread in threads]:
        fs += f
    Rcomplete = sum(ds)/ sum(fs)
    rCompleteLabel['text'] = '{:6.4f}'.format(Rcomplete)
    if compileMap.get():
        compileSF()
    if cleanup.get():
        from os import listdir, remove
        for file in listdir('./'):
            if file.startswith('.k_set'):
                remove(file)
    global IDLE
    IDLE = True


class WorkerThread(threading.Thread):
    def __init__(self, ID, queue, msgQueue, instructionFile, hklFilePath, numberOfRuns):
        super(WorkerThread, self).__init__()
        self.ID = ID
        self.queue = queue
        self.msgQueue = msgQueue
        self.insFile = instructionFile
        self.hklFilePath = hklFilePath
        self.numberOfRuns = numberOfRuns
        self.ds = []
        self.fs = []

    def run(self):
        while not exitFlag:
            lock.acquire()
            if self.queue.empty():
                lock.release()
                break
            data = self.queue.get()
            lock.release()
            self.process(data)

    def process(self, data):
        data, m = data
        name = path.splitext(data)[0]
        insName = name + '.ins'
        hklName = name + '.hkl'
        # shutil.copyfile(insFile.get(), insName)
        try:
            os.symlink(self.hklFilePath, hklName)
        except:
            import win32file
            win32file.CreateSymbolicLink(self.hklFilePath, hklName, 1)
        with open(insName, 'w') as rp:
            rp.write(self.insFile)
        try:
            call([path.join(sys._MEIPASS,'shelxl'), '-t1', '-g{}'.format(self.numberOfRuns), '-m{}'.format(m), name],
                 stdout=FNULL)
        except:
            call(['shelxl', '-t1', '-g{}'.format(self.numberOfRuns), '-m{}'.format(m), name], stdout=FNULL)
        # call(['shelxl', '-t1', name])
        with open(name+'.lst', 'r') as lstFile:
            for line in lstFile.readlines():
                if 'Nfree(all)' in line:
                    line = [_ for _ in line.split() if _]
                    d = float(line[3])
                    f = float(line [5])
                    self.ds.append(d)
                    self.fs.append(f)

        msgLock.acquire()
        if self.msgQueue.empty():
            self.msgQueue.put(1)
        else:
            i = self.msgQueue.get() + 1
            self.msgQueue.put(i)
            # print self.ID, i
        msgLock.release()


def percentScale(event):
    nFree.set(int(nHKL.get()*float(fracFree.get())/100.))
    try:
        nRunsLabel['text'] = '{} runs'.format(nHKL.get() / nFree.get())
    except ZeroDivisionError:
        nRunsLabel['text'] = '# runs'


def setScale(event):
    n = float(nFree.get())
    try:
        fracFree.set(n/nHKL.get()*100)
    except ZeroDivisionError:
        fracFree.set(0.1)

    try:
        nRunsLabel['text'] = '{} runs'.format(nHKL.get() / nFree.get())
    except ZeroDivisionError:
        nRunsLabel['text'] = '# runs'


def compileSF():
    from makeMap import makeMap
    makeMap('.k_')


def setStatus(msg):
    status['text'] = msg


def gui():
    from Tkinter import Tk, Label, Entry,Button, Scale, Checkbutton,W,HORIZONTAL, Frame, StringVar, IntVar, DoubleVar, Radiobutton, BooleanVar, E

    global root
    root = Tk()
    root.wm_title("Compute R_complete")
    line = 0

    global insFile, hklFile, nHKL, nParams, nHKLLabel, fracFree, status, nParamsLabel, nCPU, rCompleteLabel, cycles, lsType, cleanup,nFree, nRunsLabel, mergeCheck, compileMap
    insFile = StringVar()
    hklFile = StringVar()
    nHKL = IntVar()
    nParams = IntVar()
    nFree = IntVar()
    fracFree = DoubleVar()
    fracFree.set(5.0)
    nCPU = IntVar()
    nCPU.set(maxCPU)
    cycles = IntVar()
    cycles.set(10)
    lsType = IntVar()
    lsType.set(1)
    cleanup = BooleanVar()
    cleanup.set(True)
    mergeCheck = BooleanVar()
    mergeCheck.set(True)
    compileMap = BooleanVar()
    compileMap.set(True)

    Label(root, text='Instruction File:').grid(row=line, column=0, sticky=E)
    Entry(root, textvariable=insFile).grid(row=line, column=1)
    Button(root, text='Browse', command=browseINS).grid(row=line, column=2)

    line += 1

    Label(root, text='Reflection File:').grid(row=line, column=0, sticky=E)
    Entry(root, textvariable=hklFile).grid(row=line, column=1)
    Button(root, text='Browse', command=browseHKL).grid(row=line, column=2)

    # line += 1
    # Checkbutton(root, var=mergeCheck, text='Merge Reflections').grid(row=line, column=1, sticky=W)
    line += 1
    Button(root, text='Load', command=load).grid(row=line, columnspan=3)
    line += 1

    Frame(root, height=20).grid(row=line)

    line += 1

    Label(root, text='# of reflections:').grid(row=line, sticky=E)
    nHKLLabel = Label(root, text='???')
    nHKLLabel.grid(row=line, column=1, sticky=W)


    line += 1

    Label(root, text='# of atoms:').grid(row=line, sticky=E)
    nParamsLabel = Label(root, text='???')
    nParamsLabel.grid(row=line, column=1, sticky=W)

    line += 1

    Frame(root, height=20).grid(row=line)

    line += 1

    Label(root, text='Select Parameters').grid(row=line, column=1)
    line += 1

    Frame(root, height=20).grid(row=line)
    line += 1

    Label(root, text='# of free reflections:').grid(row=line, sticky=E)
    nFreeEntry = Entry(root, width=5, textvariable=nFree)
    nFreeEntry.grid(row=line, column=1, sticky=W)
    nFreeEntry.bind('<Return>', setScale)
    nRunsLabel = Label(root, text='# runs')
    nRunsLabel.grid(row=line, column=2)

    line += 1

    Label(root, text='% of free reflections:').grid(row=line, column=0, sticky=E)
    w = Scale(root, from_=0.1, to=10.0, resolution=0.1, orient=HORIZONTAL, length=200, var=fracFree, command=percentScale)
    w.grid(row=line, column=1, columnspan=2, sticky=W)


    line += 1


    Label(root, text='stable <-------------------------------> fast').grid(row=line, column=1, columnspan=2, sticky=W)

    line += 1
    Frame(root, height=10).grid(row=line)


    line += 1

    Label(root, text='Refinement cycles:').grid(row=line, column=0, sticky=E)
    ls = Scale(root, from_=0, to=50, resolution=1, orient=HORIZONTAL, length=200, var=cycles)
    ls.grid(row=line, column=1, columnspan=2, sticky=W)

    line += 1


    Label(root, text='fast <--------------------> less model bias').grid(row=line, column=1, columnspan=2, sticky=W)

    line += 1
    Frame(root, height=10).grid(row=line)


    line += 1
    Label(root, text='# of CPUs:').grid(row=line, column=0, sticky=E)
    ww = Scale(root, from_=1, to=maxCPU, orient=HORIZONTAL, length=200, var=nCPU)
    ww.grid(row=line, column=1, columnspan=2, sticky=W)

    line += 1

    Label(root, text='Refinement Type:').grid(row=line, column=0, sticky=E)
    Radiobutton(root, text='CGLS', var=lsType, value=1).grid(row=line, column=1, sticky=W)
    Radiobutton(root, text='L.S.', var=lsType, value=2).grid(row=line, column=2, sticky=W)

    line += 1
    Frame(root, height=10).grid(row=line)
    line += 1

    Label(root, text='Compile map:').grid(row=line, column=0, sticky=E)
    Checkbutton(root, var=compileMap).grid(row=line, column=1, sticky=W)

    line += 1
    Label(root, text='Cleanup:').grid(row=line, column=0, sticky=E)
    Checkbutton(root, var=cleanup).grid(row=line, column=1, sticky=W)

    line += 1

    Button(root, text='RUN', command=run, width=25).grid(row=line, columnspan=3)

    line += 1
    Frame(root, height=20).grid(row=line)
    line += 1

    Label(root, text='R_complete:').grid(row=line, column=0, sticky=E)
    rCompleteLabel = Label(root, text='???')
    rCompleteLabel.grid(row=line, column=1, sticky=W)

    line += 1

    Frame(root, height=20).grid(row=line)

    line += 1

    Label(root, text='Status:').grid(row=line, column=0, sticky=E)
    status = Label(root, text='Idle... Please load files.')
    status.grid(row=line, column=1, columnspan=2, sticky=W)
    global IDLE
    IDLE = True

    root.mainloop()


if __name__ == '__main__':
    gui()
