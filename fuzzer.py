file_list = ['./fuzz/1.pdf', './fuzz/2.pdf', './fuzz/3.pdf', './fuzz/4.pdf',
             './fuzz/5.pdf', './fuzz/6.pdf', './fuzz/7.pdf', './fuzz/8.pdf',
             './fuzz/9.pdf', './fuzz/10.pdf', './fuzz/11.pdf', './fuzz/12.pdf',
             './fuzz/13.pdf','./fuzz/14.pdf','./fuzz/15.pdf','./fuzz/16.pdf',
             './fuzz/17.pdf', './fuzz/18.pdf',
             ]
 
apps = ['/usr/bin/xpdf']
 
fuzzFactor = 250
num_tests = 10000
 
import math
import random
import string
import subprocess
import time
import os
 
def randomChars():
    "returns a string of 15 random chars for unique file names"
    chars = string.lowercase + string.uppercase + string.digits
    randomStr = ''.join([random.choice(chars) for i in range(15)])
    return randomStr
 
# keeps track of how many total iterations, and how many cause a crash
count, crash = 0, 0
 
# text file for logging crashes
log = open('./fuzz/log.txt', 'w')
 
# keeps track of crash count for each file; initialize all files to 0
file_crash_count = dict((name[7:], 0) for name in file_list)
 
start = time.time()
for i in range(num_tests):
    file_choice = random.choice(file_list)
    fuzz_output = './fuzz/fuzzed' + randomChars() + '.pdf'
    app = apps[0]
    buf = bytearray(open(file_choice, 'rb').read())
    numwrites = random.randrange(math.ceil((float(len(buf))/fuzzFactor))) + 1
 
    for j in range(numwrites):
        rbyte = random.randrange(256)
        rn = random.randrange(len(buf))
        buf[rn] = "%c" % (rbyte)
 
    open(fuzz_output, 'wb').write(buf)
    process = subprocess.Popen([app, fuzz_output])
    percent_complete = (float(count) / num_tests) * 100
    os.system('clear')
    print 'Complete: ' +  str(percent_complete) + '%'
    time.sleep(.8)
    crashed = process.poll()
    # if program crashes with exit code other than 1, save file and log file
    # name + original file + exit code. Otherwise delete the file
    if not crashed:
        process.terminate()
        os.remove(fuzz_output)
    elif crashed != 1:
        file_choice = file_choice[7:]   # get rid of file path
        file_crash_count[file_choice] += 1
        log.write('File name: ' + fuzz_output[7:] + '\n')
        log.write('Original file: ' + file_choice + '\n')
        log.write('Exit code: ' + str(crashed) + '\n\n')
        crash += 1
    else:
        os.remove(fuzz_output)
    count += 1
 
# Write various statistics to log
end = time.time()
time_taken = int(end-start)
 
log.write('Time taken (seconds): ' + str(time_taken) + '\n')
log.write('Total iterations: ' + str(count) + '\n')
log.write('Total crashes with exit code other than 1: ' + str(crash) + '\n\n')
 
sorted_file_counts = sorted([f for f in file_crash_count], reverse=True,
                            key=lambda x: file_crash_count[x])
 
log.write('Crash count for files: ' + '\n')
 
for name in sorted_file_counts:
    log.write(name + ': ' + str(file_crash_count[name]) + '\n')
 
log.close()