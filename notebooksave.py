
import pandas as pd
Tweetdf = pd.read_csv('emoji.txt', error_bad_lines=False, lineterminator='\n', delimiter='\n', nrows=5000000)
Tweetdf.columns = ['Tweets']

import emoji
from collections import Counter

def extract_emojis(s):
  return ''.join(set(c for c in s if c in emoji.UNICODE_EMOJI['en']))

def count_emojis(s):
  return len([i for i in s])

Tweetdf['Emojis'] = Tweetdf['Tweets'].apply(extract_emojis)
Tweetdf = Tweetdf.drop(['Tweets'], axis=1)

myEmojis = Counter([emoji for arr in Tweetdf['Emojis'].tolist() for emoji in arr])

CUT = len(Tweetdf) / 10000

def cut_rare_emojis(s):
    myList = []
    for i in s:
        if myEmojis[i] > CUT:
            myList.append(i)
    return "".join(myList)
        
Tweetdf['Emojis'] = Tweetdf['Emojis'].apply(cut_rare_emojis)

Tweetdf['nEmojis'] = Tweetdf['Emojis'].apply(count_emojis)
Tweetdf = Tweetdf[Tweetdf['nEmojis'] >= 2].reset_index(drop=True)

emojis = {}

for indx, row in Tweetdf.iterrows():
    for i in row['Emojis']:
        if i not in emojis:
            emojis[i] = [{j.strip():1 for j in row['Emojis']}, 1]

        else:
            emojis[i][1] += 1
            for j in row['Emojis']:
                eStrip = j.strip()
                if eStrip in emojis[i][0]:
                    emojis[i][0][eStrip] += 1

                else:
                    emojis[i][0][eStrip] = 1

for key, val in emojis.items():
    val[0].pop(key)

EmojiData = {
    'Emojis': [i for i in emojis.keys()],
    'With': [i for i, j in emojis.values()],
    'n': [j for i, j in emojis.values()]
}

Emojidf = pd.DataFrame(EmojiData)
Emojidf.to_csv('emojidf.csv')


def getDistance(e1, e2):
    B = len(Tweetdf)
    N1 = e1['n']
    N2 = Emojidf.loc[Emojidf.index[Emojidf['Emojis'] == e2].values[0], 'n']
    T = e1['With'].get(e2, 0)
    Z = N1 * N2 / B
    M = min(N1, N2)
    R = (T - M) / (Z - M)
    return R ** 2


import random

shuffleData = list(Emojidf.iterrows())
random.shuffle(shuffleData)
shuffleData = [row for idx, row in shuffleData]

myClusters = [{'🤔': 0}, {'🌸': 0}, {'🐾': 0}, {'🍰': 0}, {'🎧': 0}]

for row in shuffleData:
    emoji = row['Emojis']
    if emoji not in [e for cl in myClusters for e in cl.keys()]:
        eCluster = {idx: [] for idx in range(len(myClusters))}
        for idx, i in enumerate(myClusters):
            for j in i.keys():
                dis = getDistance(row, j)
                eCluster[idx].append(dis)

        meanDis = [sum(eCluster[i]) / len(myClusters[i]) for i in range(len(myClusters))]
        eIdx = meanDis.index(min(meanDis))
        for idx, i in enumerate(myClusters[meanDis.index(min(meanDis))].keys()):
            myClusters[eIdx][i] += eCluster[eIdx][idx]
        myClusters[eIdx][emoji] = sum(eCluster[eIdx])

for idx, i in enumerate(myClusters):
    print(f'\n{idx+1}')
    print(''.join(i.keys()))

print(myClusters)
print(len(Tweetdf))