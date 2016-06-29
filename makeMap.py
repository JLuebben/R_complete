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
                    # triple = tuple([int(i) for i in line.split()[:3]])
                    # if triple in flaggedIndices:
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

