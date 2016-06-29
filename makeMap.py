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
                        # read = False
                        break
                    triple = tuple([int(i) for i in line.split()[:3]])
                    if triple in flaggedIndices:
                        data.append(line)
                elif first:
                    data.append(line[:-1])
                if '_refln_phase_calc' in line:
                    read = True
        first = False
    with open(output, 'w') as outFile:
        outFile.write('\n'.join(data))

