import pandas as pd
import random
from copy import deepcopy

Emojidf = pd.read_csv('emoji.csv')

class Cluster:
    def __init__(self, data, startEmojis):
        self.data = data
        self.startEmojis = startEmojis
        self.totalMeanDis = 1
        self.minDis = [[], 1]
        self.myClusters = self.startCluster()
    
    def startCluster(self):
        myClusters = [{i:0} for i in self.startEmojis]
        re, myClusters = self.algoCluster(myClusters, data=self.data, badLater=True)
        print('badLater!')
        totalMeanDis, myClusters = self.algoCluster(myClusters, data=re)
        self.totalMeanDis = totalMeanDis
        return myClusters
    
    def rearrangeCluster(self, n, badLater=False):
        myClusters = deepcopy(self.myClusters)
        re = []
        for cluster in myClusters:
            lastEmojis = list(cluster.keys())[n:]
            for i in lastEmojis:
                cluster.pop(i)
                lastRow = Emojidf.loc[Emojidf.index[Emojidf['Emojis'] == i].values[0]]
                re.append(lastRow)
                for key in cluster.keys():
                    cluster[key] -= self.getDistance(lastRow, key)
        
        random.shuffle(re)
        if badLater:
            re, myClusters = self.algoCluster(myClusters, data=re, badLater=True)
            print('badLater!')
        totalMeanDis, myClusters = self.algoCluster(myClusters, data=re)
        return myClusters, totalMeanDis
    
    def getDistance(self, e1, e2):
        B = 6558070
        N1 = e1['n']
        N2 = Emojidf.loc[Emojidf.index[Emojidf['Emojis'] == e2].values[0], 'n']
        T = eval(e1['With']).get(e2, 0)
        Z = N1 * N2 / B
        M = min(N1, N2)
        D = (T - M) / (Z - M)
        return D ** 2
    
    def algoCluster(self, myClusters, data, badLater=False):
        reList = []
        for row in data:
            emoji = row['Emojis']
            if emoji not in [e for cl in myClusters for e in cl.keys()]:
                eCluster = {idx: [] for idx in range(len(myClusters))}
                for idx, i in enumerate(myClusters):
                    for j in i.keys():
                        dis = self.getDistance(row, j)
                        if dis < self.minDis[1]:
                            self.minDis[1] = dis
                            self.minDis[0] = [row, j]
                        eCluster[idx].append(dis)

                meanDis = [sum(eCluster[i]) / len(myClusters[i]) for i in range(len(myClusters))]
                if badLater and min(meanDis) >= .8:
                    reList.append(row)

                else:
                    eIdx = meanDis.index(min(meanDis))
                    for idx, i in enumerate(myClusters[meanDis.index(min(meanDis))].keys()):
                        myClusters[eIdx][i] += eCluster[eIdx][idx]
                    myClusters[eIdx][emoji] = sum(eCluster[eIdx])
                    print(f"{emoji} -> {meanDis.index(min(meanDis)) + 1}")

        totalmeandis = 0
        for idx, i in enumerate(myClusters):
            j = dict(sorted(i.items(), key=lambda item: item[1]))
            totalmeandis += sum(i.values()) / max(len(i.values()) - 1, 1) / max(len(i.values()), 1)
            myClusters[idx] = j
        totalmeandis /= len(myClusters)
            
        if badLater:
            return reList, myClusters

        return totalmeandis, myClusters
    
    def summarizeCluster(self):
        for idx, i in enumerate(self.myClusters):
            print(f'\n{idx+1}')
            print(''.join(i.keys()))
        print(f'\n{self.totalMeanDis}')

if __name__ == '__main__':
    shuffleData = list(Emojidf.iterrows())
    random.shuffle(shuffleData)
    shuffleData = [row for idx, row in shuffleData]
    cluster = Cluster(shuffleData, ['🤔', '♀', '🌸', '🐾', '🍰', '🎧', '🏆', '👉', '🚨', '🎥'])
    print('finished!')
    print(cluster.totalMeanDis)
    newCluster, new = cluster.rearrangeCluster(20, badLater=True)
    cluster.myCluster = newCluster
    newCluster, new = cluster.rearrangeCluster(-15)
    while new < cluster.totalMeanDis:
        cluster.myCluster, cluster.totalMeanDis = newCluster, new
        newCluster, new = cluster.rearrangeCluster(-15)
    print(cluster.summarizeCluster())