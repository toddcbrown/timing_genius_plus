from datetime import datetime as dt
import pandas as pd
import numpy as np

print('\n')

Bib = []
Time = []
Name = []
active = True
a = np.nan
Start = []
f = True

print('Timing Genius Plus 1.1\n(c)Todd Brown 2022\n')
while f is True:
    BIBS = input(
        'Path of name/bibs ".csv" file (optional)\nHit "Enter" if names:bib file not to be used:'
    )
    if len(BIBS) < 1:
        BIB = pd.DataFrame()
        f = False
    if len(BIBS) == 1:
        BIBS = pd.read_csv('tt_times.csv')
        f = False
    else:
        try:
            BIBS = pd.read_csv(BIBS)
            f = False
        except:
            print('*no file found*')

laps = int(input('Max laps to be recorded: '))
if laps < 2:
    laps = 2

# Create Blank Dict of Laps for DataFrame
Laps = {}
for i in range(1, laps + 1):
    Laps['lap ' + str(i)] = list()

#Create Empty DataFrame
Lapsdf = pd.DataFrame(index=range(300))
Lapsdf['Bib'] = np.nan
Lapsdf['lap 0'] = np.nan
for i in Laps.keys():
    Lapsdf[i] = np.nan

print(
    '\nDirections:\n1. Enter bib number as racer crosses line.\n2. Type "end" when done'
)
start = input('3. Hit "Enter" at TT start')
start = dt.now()
print('\nOn your mark, get set, go!\nClock has started!\n\a')

while active:
    if a != 'end':
        a = input('\nBIB: ')
        Bib.append(a)
        Time.append(dt.now() - start)
        try:
            name = BIBS.fullname.loc[BIBS.bib == int(a)].values[0]
            print(name, a, dt.now() - start)
            Name.append(name)
        except:
            print(
                a,
                "***NO NAME***",
                dt.now() - start,
            )
            Name.append(np.nan)
        times = pd.DataFrame({'Bib': Bib, 'Time': Time, 'Name': Name})
        times.to_csv('backup.csv', index=False)
    else:
        active = False

count = 0


def remove_outlier(c):
    differences = np.diff(c).tolist()
    loc = differences.index(min(differences)) + 1
    c.pop(loc)


for i in times.Bib.unique():
    b = [i]
    b.append(0)  ##start time
    timeslist = [x.total_seconds() for x in times.Time[times.Bib == i]]
    while len(timeslist) > laps:
        remove_outlier(timeslist)
        print(
            'NOTICE: bib # %s ; extra lap recorded; outlier lap removed. Lap in backup.csv file'
            % i)
    [b.append(x) for x in timeslist]
    leftover = laps - len(b) + 2  # 2 for Bib and start
    [b.append(0) for x in range(leftover)]
    Lapsdf.loc[count] = b
    count += 1

Lapsdf.to_csv('tt_final_%s.csv' % dt.now(), index=False)
pd.DataFrame([start]).to_csv('start_time_%s.csv' % dt.now(), index=False)


def zero(x):
    if x < 0:
        return 0
    else:
        return x


def minutes(x):
    return str(pd.Timedelta(round(x, 0), 'S')).split(' ')[-1]


df = Lapsdf.copy()
bibs = df.Bib
df = df.drop(columns='Bib')
df = df.dropna()
df = df.diff(axis=1).drop(columns='lap 0')
for i in df.columns:
    df[i] = df[i].apply(zero)
total = np.sum(df, axis=1).to_list()
means = np.mean(df.replace(0, np.nan), axis=1).to_list()
mins = np.min(df.replace(0, np.nan), axis=1).to_list()
best2 = [
    sum(df.replace(0, np.nan).loc[i].sort_values()[:2].to_list())
    for i in df.index
]
df['total time'] = total
df['mean lap'] = means
df['best lap'] = mins
df['best 2'] = best2
df['bib'] = bibs
cols = list(df.columns)
cols = [cols[-1]] + cols[:-1]
df = df[cols]

name = []
for i in df.index:
    try:
        name.append(BIBS.fullname.loc[BIBS.bib == int(df.bib[i])].values[0])
    except:
        name.append('none')
df['name'] = name
cols = list(df.columns)
cols = [cols[-1]] + cols[:-1]
df = df[cols]

for i in df.columns[2:]:
    df[i] = df[i].apply(minutes)

df.sort_values('bib').to_csv('final_times.csv', index=False)
