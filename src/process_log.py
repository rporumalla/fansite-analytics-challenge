import sys, os, time, re, pytz
from datetime import datetime
from collections import Counter

class processEntries:
    """
        Store host, resource, visit time and status code details into the instance variables.
        The data in the variables will be used to print the output desired by various features.
    """

    def __init__(self):
        # host data required to solve Feature 1
        self.hosts = {}
        # resources data required to solve Feature 2
        self.resources = {}
        # site visit times data required to solve Feature 3
        self.siteVistedTimes = []
        # all the site attempt details for Feature 4 - host name, status code, visit time
        self.siteAttemptDetails = {}

    # stores the host details in the hosts dictionary with host name as key and number of times they accessed the site
    # as its value
    def activeHosts(self, entry):
        hostNames = self.hosts.keys()
        # if host name (key) not present in dictionary set the value to 1 or else increment the value by 1
        if entry not in hostNames:
            self.hosts[entry] = 1
        else:
            self.hosts[entry] += 1

    # store the resource details in the resources dictionary with resource accessed as key and bytes sent as its value
    def topResources(self, entry1, entry2):
        res = self.resources.keys()
        # if resource name (key) not present in dictionary set the value to bytes sent or else increment the value by the
        # number of bytes sent
        if entry1 not in res:
            self.resources[entry1] = int(entry2)
        else:
            self.resources[entry1] += int(entry2)

    # convert the date time entries to epoch time and add it to the 'siteVistedTimes' list
    def siteVisits(self, dateEntry):
        self.siteVistedTimes.append(convertToEpoch(dateEntry))

    # add the epoch time, status code and the line entry to a list of tuples
    def siteAttempts(self, line, host, date, statusCode):
        hostNames = self.siteAttemptDetails.keys()
        if host not in hostNames:
            self.siteAttemptDetails[host] = [tuple((convertToEpoch(date), statusCode, line))]
        else:
            self.siteAttemptDetails[host].append(tuple((convertToEpoch(date), statusCode, line)))

    # add host names with failed login attempts to a list
    def findFailedAttempts(self):
        keys = []
        if self.siteAttemptDetails:
            for key, value in prEntries.siteAttemptDetails.items():
                for item in value:
                    if item[1] == '401':
                        keys.append(key)
                        break
        return keys

# convert date time string to epoch time
def convertToEpoch(dateString):
    pattern = '%d/%b/%Y:%H:%M:%S'
    return int(time.mktime(time.strptime(dateString, pattern)))

# convert epoch time to date time string
def convertEpochToDate(epoch, offset):
    pattern = '%d/%b/%Y:%H:%M:%S'
    return datetime.fromtimestamp(epoch).strftime(pattern) + ' ' + offset

#
def uniqueEntries(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

# find number of entries till 5 minutes after 3 consecutive failed logins
# The function assumes that the array is sorted
def findHourCounts(lst, d, n):

    size = len(lst)
    hours = {}
    hour_beginning = []
    z = 0

    # Initialize positions of two elements
    i, j = 0, 1

    # Search for a pair
    while i < size and j < size:
        count = d[lst[i]]
        for t in range(count):
            if j - i in [0, 1]:
                x = time.gmtime(lst[i]).tm_min * 60 + time.gmtime(lst[i]).tm_sec
                z = lst[i] - x + 1
                while True:
                    if z not in hour_beginning:
                        hour_beginning.append(z)

                        hours[z] = d[lst[i]]
                        break
                    z += 1

                if i > 0:
                    for k in range(i):
                        if z <= lst[k]:
                            hours[z] += d[lst[k]]
            if lst[j] in d and i != size-1:
                hours[z] += d[lst[j]]
            j += 1

            if (j == size) or (i != j and lst[j] - lst[i] > n):
                if t == count-1:
                    i += 1
                if i == size -1:
                    j = i
                else:
                    j = i + 1

    return hours


if __name__ == '__main__':
    bufsize = 65536
    # path = '../log_input/log.txt'
    pacific_time = pytz.timezone("America/Los_Angeles")
    prEntries = processEntries()
    utcOffset = ''
    remove_chars = len(os.linesep)
    # input file
    inputFile = sys.argv[1]
    # output files
    outputFile1 = sys.argv[2]
    outputFile2 = sys.argv[3]
    outputFile3 = sys.argv[4]
    outputFile4 = sys.argv[5]
    # outputFile1 = '../log_output/hosts.txt'
    # outputFile2 = '../log_output/resources.txt'
    # outputFile3 = '../log_output/hours.txt'
    # outputFile4 = '../log_output/blocked.txt'
    with open(inputFile) as infile:
        while True:
            lines = infile.readlines(bufsize)
            if not lines:
                break
            for line in lines:
                line = re.sub(' +', ' ', line)
                line = re.sub('\n+', '', line)
                entries = line.split(' ')
                host = entries[0]
                resource = entries[6]
                date = entries[3].replace('[', '')
                utcOffset = entries[4].replace(']', '')
                if 'HTTP' in entries[7]:
                    statusCode = entries[8]
                    bytes = entries[9]
                else:
                    statusCode = entries[7]
                    bytes = entries[8]
                if not bytes.isdigit():
                    bytes = 0
                prEntries.activeHosts(host)
                prEntries.topResources(resource, bytes)
                prEntries.siteVisits(date)
                prEntries.siteAttempts(line, host, date, statusCode)

    # Feature1
    target1 = open(outputFile1, "w+")
    target1.truncate()
    hostContents = Counter(prEntries.hosts)
    # count = 0
    for k, v in hostContents.most_common(10):
        target1.write(k)
        target1.write(",")
        target1.write(str(v))
        target1.write("\n")


    # Feature2
    target2 = open(outputFile2, "w+")
    target2.truncate()
    resourceContents = Counter(prEntries.resources)
    for k, v in resourceContents.most_common(10):
        target2.write(k)
        target2.write("\n")


    # Feature 3
    siteVistedTimes = uniqueEntries(prEntries.siteVistedTimes)
    dupeCounts = dict(Counter(prEntries.siteVistedTimes))
    finalHourCounts = findHourCounts(siteVistedTimes, dupeCounts, 3600)
    target3 = open(outputFile3, "w+")
    target3.truncate()
    hourContents = Counter(finalHourCounts)
    for k, v in hourContents.most_common(10):
        target3.write(convertEpochToDate(k, utcOffset))
        target3.write(",")
        target3.write(str(v))
        target3.write("\n")


    # Feature 4
    target4 = open(outputFile4, "w+")
    target4.truncate()
    validFailedEntries = prEntries.findFailedAttempts()
    if len(validFailedEntries) > 0:
        for key in prEntries.siteAttemptDetails.keys():
            if key in validFailedEntries:
                prEntries.siteAttemptDetails[key].sort(key=lambda tup: tup[0])
                hostEntries = prEntries.siteAttemptDetails[key]
                noEntries = len(prEntries.siteAttemptDetails[key])
                failLoginIdx = [i for i, v in enumerate(prEntries.siteAttemptDetails[key]) if v[1] == '401']
                failLoginIdxGroup = [failLoginIdx[n:n+3] for n in range(len(failLoginIdx)-2) if failLoginIdx[n+2]-failLoginIdx[n]==2]
                idxGroupSize = len(failLoginIdxGroup)
                if idxGroupSize > 1:
                    p = 0
                    while True:
                        p += 1
                        if hostEntries[failLoginIdxGroup[p][0]][0] - hostEntries[failLoginIdxGroup[0][2]][0] <= 300:
                            del failLoginIdxGroup[p]
                            p -= 1
                        if p == len(failLoginIdxGroup)-1:
                            break
                idxGroupSize = len(failLoginIdxGroup)
                if idxGroupSize > 0:
                    for idx in failLoginIdxGroup:
                        if idx[2] < noEntries-1:
                            timeDiff1 = hostEntries[idx[2]][0] - hostEntries[idx[0]][0]
                            time1 = hostEntries[idx[2]][0]
                            if timeDiff1 <= 20:
                                i = idx[2]
                                while True:
                                    i += 1
                                    timeDiff2 = hostEntries[i][0] - time1
                                    if timeDiff2 > 300:
                                        break
                                    target4.write(hostEntries[i][2])
                                    if i == noEntries-1:
                                        break
                                    target4.write('\n')