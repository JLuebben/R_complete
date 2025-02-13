import multiprocessing

from subprocess import call
import threading
try:
    import Queue
except ImportError:
    import queue as Queue
import sys
from os import path
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


def load():
    global IDLE
    if not IDLE:
        return
    IDLE = False
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
    try:
        from tkFileDialog import askopenfilename
    except ImportError:
        from tkinter.filedialog import askopenfilename
    insFile.set(askopenfilename())
    hklGuess = path.splitext(insFile.get())[0]+'.hkl'
    if path.isfile(hklGuess) and not hklFile.get():
        hklFile.set(hklGuess)


def browseHKL():
    try:
        from tkFileDialog import askopenfilename
    except ImportError:
        from tkinter.filedialog import askopenfilename
    hklFile.set(askopenfilename())
    resGuess = path.splitext(hklFile.get())[0]+'.res'
    if insFile.get():
        return
    if path.isfile(resGuess):
        insFile.set(resGuess)

    insGuess = path.splitext(hklFile.get())[0]+'.ins'
    if path.isfile(insGuess):
        insFile.set(insGuess)


class MockType(dict):
    def __init__(self, value=False, silent=True, prefix=''):
        self.value = value
        self.silent = silent
        self.prefix = prefix
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
    def __call__(self, *args, **kwargs):
        pass
    def after(self, *args):
        pass
    def __getitem__(self, item):
        return self.value
    def __setitem__(self, key, value):
        self.value = value
        if not self.silent:
            print('{}{}'.format(self.prefix, value))

def showHead():
    print('''
#################################################
#                   R_complete                  #
#    A tool to compute R_complete with SHELXL   #
#                                               #
# Please cite:                                  #
# J Luebben, T Gruene, PNAS 112 (29), 8999-9003 #
#################################################

    USAGE: R_complete [options] filename

Call program without file name or with '--help'
for additional information.
''')

def showHelp():
    print('''
OPTIONS:
    n[50]:    Number of free reflections in each run.
    i[20]:    Number of refinement cycles.
    l[CGLS]:  Optimization method. CGLS or L.S.
    u[all]:   Number of CPUs used.
    h[*.hkl]: Name of reflection file.
    f:        Compile an unbiased .fcf file.
    w:        WIGL parameters before refining.

The sequence of options and filename on the
command line are irrelevant.
''')

def setOptions(options, key):
    options[key] = True
    return False


def noGUI():
    showHead()
    options = {'n': 50,
               'l': 'CGLS',
               'i': 20,
               'u': maxCPU,
               'f': False,
               'w': False,
               'h': None,
               'file': '',
               'x': False}
    refSet = set(options.keys())
    from sys import argv
    if '--help' in argv:
        showHelp()
        return
    argv = [(arg, True if arg.startswith('-') and all([i in options for i in arg[1:]]) else False) for arg in argv[1:]]
    argv = [(arg, True if n and options[arg.lstrip('-')] else setOptions(options, arg.lstrip('-'))) for arg, n in argv]
    # print(argv)
    cmd = None
    for arg, n in argv:
        opt = arg.startswith('-')
        arg = arg.lstrip('-')
        if n:
            cmd = arg
            continue
        elif cmd:
            options[cmd] = arg
            cmd = None
        elif opt:
            value = arg[1:]
            options[arg[0]] = value if value else True
        else:
            if not options['file']:
                options['file'] = arg
            else:
                print('Warning: Unknown additional argument:', arg)
    diff = set(options.keys()).difference(refSet)
    if len(diff)>1:
        print('Error: Unknown option:', diff)
    if not options['file'] or not options['l'] in ('CGLS', 'L.S.'):
        print('Error: Could not parse options.')
        showHelp()
        return
    insContent = open(options['file'], 'r').readlines()
    globals()['insFile'] = MockType(options['file'])
    globals()['insContent'] = insContent
    globals()['nFree'] = MockType(options['n'])
    globals()['lsType'] = MockType(options['l'])
    globals()['cycles'] = MockType(options['i'])
    globals()['compileMap'] = MockType(options['f'])
    globals()['wigl'] = MockType(options['w'])
    globals()['nHKL'] = MockType()
    globals()['nCPU'] = MockType(options['u'])
    globals()['nHKLLabel'] = MockType()
    globals()['nParams'] = MockType()
    globals()['nParamsLabel'] = MockType()
    globals()['fracFree'] = MockType()
    globals()['status'] = MockType()
    globals()['percentScale'] = MockType()
    if options['h']:
        globals()['hklFile'] = MockType(options['h'])
    else:
        globals()['hklFile'] = MockType(options['file'][:-3]+'hkl')
    _load()
    globals()['nFree'] = MockType(options['n'])
    globals()['root'] = MockType()
    globals()['cleanup'] = MockType(True)
    globals()['rCompleteLabel'] = MockType(silent=False, prefix='R_complete:\n')
    try:
        _run()
        for thread in threads:
            thread.join()
        finish()
    except:
        print('xxxxx')
        clean()

    return rCompleteLabel.get()


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
    global insContent
    k = nFree.get()
    foundMerge = False
    foundWigl = False
    foundList = False
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

        if line[:4].upper() == 'WIGL':
            # insContent[i] = 'MERG 4\n'
            foundWigl = True

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

    if not foundWigl and wigl.get():
        for i, line in enumerate(insContent):
            if line[:4].upper() == 'L.S.' or line[:4].upper() == 'CGLS':
                insContent = insContent[:i+1] + ['WIGL\n'] + insContent[i+1:]
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
    for n in range(nFiles):
        n += 1
        queue.put(('.k_set{:0>4}.hkl'.format(str(n)),n))
    for i in range(nCPU.get()):
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
        clean()
    global IDLE
    IDLE = True

def clean():
    from os import listdir, remove
    for file in listdir('./'):
        if file.startswith('.k_set'):
            remove(file)


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
            #import win32file
            #win32file.CreateSymbolicLink(self.hklFilePath, hklName, 1)
            import shutil
            shutil.copy(self.hklFilePath, hklName)
        with open(insName, 'w') as rp:
            rp.write(self.insFile)
        try:
            call([path.join(sys._MEIPASS,'shelxl'), '-t1', '-g{}'.format(self.numberOfRuns), '-m{}'.format(m), name],
                 stdout=FNULL)
        except:
            call(['shelxl', '-t1', '-g{}'.format(self.numberOfRuns), '-m{}'.format(m), name], stdout=FNULL)
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
        msgLock.release()


def percentScale(event):
    nFree.set(int(nHKL.get()*float(fracFree.get())/100.))
    try:
        nRunsLabel['text'] = '{} runs'.format(int(nHKL.get() / nFree.get()))
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
    makeMap('.k_')


def setStatus(msg):
    status['text'] = msg


def gui():
    try:
        from Tkinter import Tk, Label, Entry,Button, Scale, Checkbutton,W,HORIZONTAL, Frame, StringVar, IntVar, DoubleVar, Radiobutton, BooleanVar, E
    except ImportError:
        from tkinter import Tk, Label, Entry,Button, Scale, Checkbutton,W,HORIZONTAL, Frame, StringVar, IntVar, DoubleVar, Radiobutton, BooleanVar, E

    global root
    root = Tk()
    root.wm_title("Compute R_complete")
    line = 0

    global insFile, hklFile, nHKL, nParams, nHKLLabel, fracFree, status, nParamsLabel, nCPU, rCompleteLabel, cycles, lsType, cleanup,nFree, nRunsLabel, mergeCheck, compileMap, wigl
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
    wigl = BooleanVar()
    wigl.set(False)

    Label(root, text='Instruction File:').grid(row=line, column=0, sticky=E)
    Entry(root, textvariable=insFile).grid(row=line, column=1)
    Button(root, text='Browse', command=browseINS).grid(row=line, column=2)

    line += 1

    Label(root, text='Reflection File:').grid(row=line, column=0, sticky=E)
    Entry(root, textvariable=hklFile).grid(row=line, column=1)
    Button(root, text='Browse', command=browseHKL).grid(row=line, column=2)

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

    # line += 1
    # Label(root, text='Wigle:').grid(row=line, column=0, sticky=E)
    # Checkbutton(root, var=wigl).grid(row=line, column=1, sticky=W)

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
    
    root.lift()
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)
    root.mainloop()

from os import listdir
from os.path import join


def makeMap(fileNameBase, dir='./', output='Rcomplete.fcf'):
    fcfFiles = [fcfFile for fcfFile in listdir(join(dir))
                if fcfFile.endswith('.fcf') and fcfFile.startswith(fileNameBase)]
    data = []
    first = True
    for fcfFile in fcfFiles:
        hklFile = fcfFile[:-3] + 'hkl'
        flaggedIndices = []
        with open(hklFile, 'r') as hkl:
            for line in hkl.readlines():
                if line[-3:-1] == '-1':
                    flaggedIndices.append(tuple([int(i) for i in line[0:14].split()]))
        with open(fcfFile, 'r') as fcf:
            read = False
            for line in fcf.readlines():
                if read:
                    line = line.rstrip(' \n')
                    if not line:
                        break
                    line = line.strip().split()
                    fCalc = '{:7.2f}'.format(float(line[5])**.5).strip()
                    line[5] = fCalc
                    line = ' ' + ' '.join(line[:-2])
                    data.append(line)
                elif first:
                    if '_refln_F_squared_calc' in line:
                        data.append(' _refln_F_calc')
                    elif '_refln_d_spacing' in line:
                        continue
                    elif '_shelx_refinement_sigma' in line:
                        pass
                    elif '_shelx_refln_list_code' in line:
                        data.append('_shelx_refln_list_code          6')
                    else:
                        data.append(line[:-1])
                if '_shelx_refinement_sigma' in line:
                    read = True
        first = False
    with open(output, 'w') as outFile:
        outFile.write('\n'.join(data)+'\n')




if __name__ == '__main__':
    from sys import argv
    if '-x' in argv:
        noGUI()

    else:
        gui()
