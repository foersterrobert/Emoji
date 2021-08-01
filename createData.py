import pandas as pd
Tweetdf = pd.read_csv('emoji.txt', error_bad_lines=False, lineterminator='\n', delimiter='\n')
Tweetdf.columns = ['Tweets']

print(Tweetdf.shape)
print(Tweetdf.head())

# Emojis aus Tweets filtern

from collections import Counter
import emoji

def extract_emojis(s):
  return ''.join(set(c for c in s if c in emoji.UNICODE_EMOJI['en']))

def count_emojis(s):
  return len([i for i in s])

Tweetdf['Emojis'] = Tweetdf['Tweets'].apply(extract_emojis)
Tweetdf = Tweetdf.drop(['Tweets'], axis=1)

myEmojis = Counter([emo for arr in Tweetdf['Emojis'].tolist() for emo in arr])

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

print(len(Tweetdf))
print(Tweetdf.head())

# Neuen Datensatz aus Emojis erstellen

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

print(Emojidf.head())

Emojidf.to_csv('emoji.csv')