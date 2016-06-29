def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0


def dummy(*args):
    print args[0]


class Data(object):
    def __init__(self, fileName, symmops, outputFileName='out.hkl', callback=dummy):
        callback('Reading input data.')
        self.data = {}
        with open(fileName, 'r') as fp:
            inputData = [HKL(line) for line in fp.readlines() if len(line) > 1 and not line.startswith('_') and not line.startswith('   0   0   0')]
        callback('Input read. Normalizing indices.')
        nR = len(inputData)
        previous = None
        normalPrevious = None
        for i, hkl in enumerate(inputData):
            if not i%5000:
                callback('Normalizing indices: {:3} %'.format(int(float(i)/ nR*100)))
            before = (hkl.h, hkl.k, hkl.l)
            hkl.normalize(symmops, previous, normalPrevious)
            previous = before
            normalPrevious = (hkl.h, hkl.k, hkl.l)
            try:
                self.data[hkl()].append((hkl.I, hkl.sigma))
            except KeyError:
                self.data[hkl()] = [(hkl.I, hkl.sigma)]
        callback('Normalizing indices: 100 %')
        callback('Sorting data.')
        indices = sorted(self.data.keys(), key=lambda v: (v[2], v[1], v[0]), reverse=False)
        callback('Sorting complete. Merging equivalents.')
        with open(outputFileName, 'w') as fp:
            for index in indices:
                values = self.data[index]
                m = median([v[0] for v in values])
                top = 0.
                ws = 0.
                ss = 0.00001
                for v, s in values:
                    d = abs(m-v)
                    if d < 1:
                        d = 1
                    w = d*s
                    top += w*v
                    ws += w
                    if not s:
                        s = 0.00001
                    ss += 1./s**2
                h, k, l = index
                fp.write('{:4}{:4}{:4} {:-7.2f} {:-7.2f}\n'.format(h, k, l, top/ws, (1./ss)**.5))
            fp.write('{:4}{:4}{:4} {:-7.2f} {:-7.2f}   {}\n'.format(0, 0, 0, 0, 0, 0))
        callback('Data merged successfully.')



class HKL(object):
    def __init__(self, line):
        self.good = True
        line = line[:-1].split()
        self.h, self.k, self.l, self.I, self.sigma = [int(i) for i in line[:3]] + [float(i) for i in line[3:]]

    def __call__(self, *args, **kwargs):
        return (self.h, self.k, self.l)

    def normalize(self, laueGroup, previous=None, previousNormal=None):
        if previous == (self.h, self.k, self.l):
            self.h, self.k, self.l = previousNormal
            return
        triples = [(self.h, self.k, self.l)]


        for symmop in laueGroup:
            h, k, l = triples[0]
            newTriple = (int(h*symmop[0] + k*symmop[3] + l*symmop[6]),
                         int(h*symmop[1] + k*symmop[4] + l*symmop[7]),
                         int(h*symmop[2] + k*symmop[5] + l*symmop[8]))
            triples.append(newTriple)

        indices = sorted(triples, key=lambda v: '{}{}{}'.format(v[2], v[1], v[0]), reverse=True)
        # if all([i == 0 for i in indices[0]]):
        #     print
        #     for i in triples: print i
        #     raw_input()
        self.h, self.k, self.l = indices[0]



# symmops = {'i': (-1, 0, 0,
#                  0, -1, 0,
#                  0, 0, -1, 1),
#            '200': (1, 0, 0,
#                    0, -1, 0,
#                    0, 0, -1, 1),
#            '020': (-1, 0, 0,
#                    0, 1, 0,
#                    0, 0, -1, 1),
#            '002': (-1, 0, 0,
#                    0, -1, 0,
#                    0, 0, 1, 1),
#            'm00': (-1, 0, 0,
#                    0, 1, 0,
#                    0, 0, 1, 1),
#            '0m0': (1, 0, 0,
#                    0, -1, 0,
#                    0, 0, 1, 1),
#            '00m': (1, 0, 0,
#                    0, 1, 0,
#                    0, 0, -1, 1),
#            '400': (1, 0, 0,
#                    0, 0, -1,
#                    0, 1, 0, 3),
#            '300': (1, 0, 0,
#                    0, .5, -.86602540,
#                    0, .86602540, .5, 2),
#            '030': (.5, 0, .86602540,
#                    0, 1, 0,
#                    -.86602540, 0, .5, 2),
#            '600': (1, 0, 0,
#                    0, .86602540, -.5,
#                    0, .5, .86602540, 5)}
#
# laueGroups = {'-1': [symmops['i']],
#               '2/m': [symmops['200'], symmops['m00'], symmops['i']],
#               'mmm': [symmops['m00'], symmops['0m0'], symmops['00m'], symmops['i'], symmops['200'], symmops['020'],
#                       symmops['002']],
#               '4/m': [symmops['400'], symmops['m00'], symmops['i']],
#               '4/mmm': [symmops['400'], symmops['m00'], symmops['0m0'], symmops['00m'], symmops['i']],
#               '-3': [symmops['i'], symmops['300']],
#               '-3/m': [symmops['i'], symmops['300'], symmops['m00']],
#               '6/m': [symmops['600'], symmops['m00']],
#               '6/mmm': [symmops['600'], symmops['m00'], symmops['0m0'], symmops['00m']],
#               'm3': [symmops['m00'], symmops['030']],
#               'm3m': [symmops['m00'], symmops['030'], symmops['00m']]}


def shelx2Symmop(fileName):
    symmops = set()
    with open(fileName, 'r') as fp:
        for line in fp.readlines():
            if line.startswith('SYMM'):
                rawops = line[5:-1].split(',')
                lines = []
                for rawop in rawops:
                    rawop = rawop.upper()
                    line = [0,0,0]
                    if '-X' in rawop:
                        line[0] = -1
                    elif 'X' in rawop:
                        line[0] = 1

                    if '-Y' in rawop:
                        line[1] = -1
                    elif 'Y' in rawop:
                        line[1] = 1

                    if '-Z' in rawop:
                        line[2] = -1
                    elif 'Z' in rawop:
                        line[2] = 1
                    lines += line
                symmops.add(tuple(lines))
    newSymmops = [(-1,0,0,
                   0,-1,0,
                   0,0,-1)]
    for symmop in symmops:
        newSymmops.append((symmop[0]*-1, symmop[1]*-1, symmop[2]*-1,
                     symmop[3]*-1, symmop[4]*-1, symmop[5]*-1,
                     symmop[6]*-1, symmop[7]*-1, symmop[8]*-1,))
    for s in newSymmops:
        symmops.add(s)
    return symmops


def mergeHKLFile(instructionFileName, reflectionFileName, outputFileName, callback=dummy):
    """
    Interface function for merging diffraction data in HKL format.
    :param instructionFileName: File name of a SHELXL instruction file.
    :param reflectionFileName: File name of an HKL file.
    :param outputFileName: Output file name. Will be HKL format.
    :param callback: Function that will get called periodically with status updates about the merging progress.
    :return: None
    """
    # symmops = shelx2Symmop(instructionFileName)
    # for i in symmops:
    #     print
    #     for chunk in xrange(3):
    #         print i[chunk*3:chunk*3+3]
    Data(reflectionFileName, shelx2Symmop(instructionFileName), outputFileName, callback=callback)


if __name__ == '__main__':
    from sys import argv
    # data = Data(argv[-1])
    # data = Data('unmerged.hkl')
    symmops = shelx2Symmop('shelx.res')
    for i in symmops:
        print
        for chunk in xrange(3):
            print i[chunk*3:chunk*3+3]
    # raw_input()
    data = Data('unmerged.hkl', symmops)
