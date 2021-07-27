# Emoji Clustering

## Das Einsortieren von Emojis anhand von Tweets

Bild: https://tattooedcrmgirl.com/2019/08/23/how-to-add-emojis-to-your-microsoft-to-do-lists/

#### 28. Juli 2021


## Inhaltsverzeichnis

### 1. Daten

##### 1.1. Erstellung eines Dataframes in Pandas

##### 1.2. Extrahieren der Emojis aus den Tweets

##### 1.3. Von Tweet-Dataframe zu Emoji-Dataframe

### 2. Clustering

##### 2.1. Die Distanzfunktion

##### 2.2. Der Algorithmus

##### 2.3. Optimierungen

### 3. Ergebnis




##### Das Ziel des Projektes ist es, Emojis anhand ihres gemeinsamen Vorkommens in

##### Tweets in N-verschiedene Cluster zu gruppieren. Im Folgenden finden Sie

##### Erklärungen zu aufbauenden Code-Snippets. Auch wenn diese für den

##### grundlegenden Clustering-Prozess ausreichend sind, ist es für das vollständige

##### Verständnis empfehlenswert, sich den ganzen Objekt-orientierten Code unter

##### https://github.com/foersterrobert/Emoji anzuschauen.

##### Wenn Sie selbst mit dem Code experimentieren möchten, können Sie sich

##### entweder den vollständigen Datensatz von https://www.kaggle.com/rexhaif/

##### emojifydata-en?select=emojitweets-01-04-2018.txt herunterladen oder die

##### anfängliche Datenmanipulation überspringen und mit dem im Repository

##### vorgefertigten emojis.csv direkt mit dem Clustering beginnen.

### 1. Daten

##### 1.1. Erstellung eines Dataframes in Pandas

##### Für die Verarbeitung mit Python erstellen wir als Erstes aus den Tweets einen

##### Dataframe in Pandas. Da einzelne Reihen z.B. durch mehrere Zeilenabstände

##### fehlerhaft sind, geben wir Pandas die zusätzlichen Argumente

##### error_bad_lines=False und lineterminator=‚\n'. So erhalten wir insgesamt einen

##### Datensatz von 18.565.846 Tweets. Mit Tweetdf.head() können wir die ersten

##### Zeilen ausgeben und den Zustand des Dataframes kontrollieren.


##### import pandas as pd

##### Tweetdf	=	pd.read_csv('emoji.txt',	error_bad_lines=False,		

##### lineterminator='\n',	delimiter='\n',	nrows= 5000000 )	

##### Tweetdf.columns	=	['Tweets']	


##### 1.2. Extrahieren der Emojis aus den Tweets

##### Im nächsten Schritt wollen wir die Emojis aus den Tweets extrahieren. Dafür

##### nutzen wir die Python-Emoji-Bibliothek. Wir wollen uns bei dem Emoji-

##### Clustering auf häufig benutzte Emojis fokussieren, weshalb wir alle Emojis

##### entfernen, die nicht durchschnittlich in jedem 10.000. Tweet vorkommen. Die

##### Häufigkeit eines Emojis ermitteln wir über ein Counter-Objekt aus der

##### eingebauten Python-Collections-Bibliothek. Nun führen wir eine zusätzliche

##### Spalte ein, die die häufigen Emojis eines Tweets zählt, und entfernen die

##### Reihen, in denen nicht mindestens 2 verschiedene häufig verwendete Emojis

##### vorkommen.


###### import emoji

###### from collections import Counter

###### def extract_emojis(s):	

###### return ''.join(set(c for c in s if c in emoji.UNICODE_EMOJI['en']))	

###### def count_emojis(s):	

###### return len([i for i in s])	

###### Tweetdf['Emojis']	=	Tweetdf['Tweets'].apply(extract_emojis)	

###### Tweetdf	=	Tweetdf.drop(['Tweets'],	axis= 1 )	

###### myEmojis	=	Counter([emoji for arr in Tweetdf['Emojis'].tolist()	for emoji in arr])	

###### CUT	=	len(Tweetdf)	/	 10000	

###### def cut_rare_emojis(s):	

###### myList	=	[]	

###### for i in s:	

###### if myEmojis[i]	>	CUT:	

###### myList.append(i)	

###### return "".join(myList)	

###### Tweetdf['Emojis']	=	Tweetdf['Emojis'].apply(cut_rare_emojis)	

###### Tweetdf['nEmojis']	=	Tweetdf['Emojis'].apply(count_emojis)	

###### Tweetdf	=	Tweetdf[Tweetdf['nEmojis']	>=	 2 ].reset_index(drop=True)


##### 1.3. Von Tweet-Dataframe zu Emoji-Dataframe

##### Für das Clustering interessieren uns vor allem die Eigenschaften der einzelnen

##### Emojis. Daher erstellen wir einen neuen Datensatz, in dem jede Reihe einem

##### Emoji samt einem Dictionary von anderen Emojis, mit denen es gepostet wird,

##### entspricht. Unter der Spalte „n“ geben wir zusätzlich an, wie oft ein Emoji

##### gepostet wurde.


###### emojis	=	{}	

###### for indx,	row in Tweetdf.iterrows():	

###### for i in row['Emojis']:	

###### if i not in emojis:	

###### emojis[i]	=	[{j.strip(): 1	 for j in row['Emojis']},	 1 ]	

###### else:	

###### emojis[i][ 1 ]	+=	 1	

###### for j in row['Emojis']:	

###### eStrip	=	j.strip()	

###### if eStrip in emojis[i][ 0 ]:	

###### emojis[i][ 0 ][eStrip]	+=	 1	

###### else:	

###### emojis[i][ 0 ][eStrip]	=	 1	

###### for key,	val in emojis.items():	

###### val[ 0 ].pop(key)	

###### EmojiData	=	{	

###### 'Emojis':	[i for i in emojis.keys()],	

###### 'With':	[i for i,	j in emojis.values()],	

###### 'n':	[j for i,	j in emojis.values()]	

###### }


## 2. Clustering

##### Nun da wir unseren Emoji-Dataframe haben, können wir mit dem Clustering

##### anfangen. Unser Ziel ist es, alle Emojis durch einen Algorithmus in getrennte

##### Kategorien einzuteilen.

##### 2.1. Die Distanzfunktion

##### Als Erstes brauchen wir eine Python-Funktion, die die Distanz zwischen 2

##### verschiedenen Emojis bestimmt.


###### def getDistance(e1,	e2):	

###### B	=	len(Tweetdf)	

###### N1	=	e1['n']	

###### N2	=	Emojidf.loc[Emojidf.index[Emojidf['Emojis']	==	e2].values[ 0 ],	'n']	

###### T	=	e1['With'].get(e2,	 0 )	

###### Z	=	N1	*	N2	/	B

###### M	=	min(N1,	N2)	

###### return	((T	-	M)	/	(Z	-	M))	**	 2	


##### Lasst uns das Ganze an dem Beispiel der Distanz zwischen 💕 & 🌸 zeigen.

##### 💕 wird 268163-mal verwendet und 🌸 56684-mal. Nach dem Reduzieren auf

##### Tweets, in denen mindestens 2 verschiedene Emojis vorkommen, besteht unser

##### Datensatz aus 6558070 Tweets. Nur durch Zufall würden die Emojis also

##### 2317,84-mal (268163 * 56684 / 6558070) gemeinsam vorkommen. Das

##### maximale gemeinsame Vorkommen wäre 56684. Die Distanz zwischen den

##### Emojis nähert sich 1, wenn ihr gemeinsames Vorkommen dem Zufall

##### entgegenkommt. Auf der anderen Seite haben die Emojis eine Distanz von 0,

##### wenn ihr gemeinsames Vorkommen dem Maximum entspricht.

##### Das wirkliche gemeinsame Vorkommen ist 9102-mal. Durch das anschließende

##### Quadrieren der Abweichung ist die Distanz zwischen 💕 & 🌸 = 0,7659.

##### Da die Funktion so später für uns von größtem Nutzen ist, stellt e1 eine Reihe

##### im Dataframe dar und e2 einen Emoji als String.


##### 2.2. Der Algorithmus

##### Nachdem es uns mit der Distanzfunktion möglich ist, zwischen allen

##### verschiedenen Emojis eine Verbindung herzustellen, brauchen wir einen

##### Algorithmus, der nun die Emojis so in Cluster einteilt, dass ein Minimum in der

##### globalen Distanz erreicht wird.

##### Die Idee ist, für den Anfang N-verschiedene Dictionaries zu erstellen, die

##### jeweils ein Emoji beinhalten und die Cluster darstellen. Der Value des Emojis im

##### Dictionary ist seine Distanz zu allen anderen Emojis im Cluster, also für den

##### Anfang 0. Nun iterieren wir über alle Emojis in unserem Emoji-Dataframe, die

##### nicht schon von Anfang an in den Clustern sind, und ermitteln für jedes Cluster

##### die durchschnittliche Distanz zu unserem Emoji. Anschließend fügen wir das

##### Emoji dem Dictionary hinzu, zu dem es die niedrigste durchschnittliche Distanz

##### hat. Der Value dieses Emojis entspricht der Summe aller Distanzen, und die

##### Values aller anderen Emojis im Cluster werden um die neue Distanz zwischen

##### ihnen und dem neuen Emoji addiert.

###### import random

###### shuffleData	=	list(Emojidf.iterrows())	

##### random.shuffle(shuffleData)

###### shuffleData	=	[row for idx,	row in shuffleData]	

##### myClusters	=	[{'🤔':	 0 },	{'🌸':	 0 },	{'🐾':	 0 },	{'🍰':	 0 },	{'🎧':	 0 }]	

###### for row in shuffleData:	

###### emoji	=	row['Emojis']	

###### if emoji not in	[e for cl in myClusters for e in cl.keys()]:	

###### eCluster	=	{idx:	[]	for idx in range(len(myClusters))}	

###### for idx,	i in enumerate(myClusters):	

###### for j in i.keys():	

###### dis	=	getDistance(row,	j)	

###### eCluster[idx].append(dis)	

###### meanDis	=	[sum(eCluster[i])	/	len(myClusters[i])	for i in range(len(myClusters))]	

###### eIdx	=	meanDis.index(min(meanDis))	

###### for idx,	i in enumerate(myClusters[meanDis.index(min(meanDis))].keys()):	

###### myClusters[eIdx][i]	+=	eCluster[eIdx][idx]	

###### myClusters[eIdx][emoji]	=	sum(eCluster[eIdx])	


##### 2.3. Optimierungen

##### Um die entstandenen Cluster unabhängiger von der Reihenfolge der

##### Einsortierungen zu machen, ist es hilfreich, als Erstes die Emojis mit besonders

##### geringen Distanzen auszuwählen. Dies geschieht, indem man in dem

##### Clustering-Algorithmus eine Distanz festlegt (ich habe den 0.8 gewählt), die ein

##### Emoji zu seinem nächsten Cluster unterbieten muss, um in Phase 1 einsortiert

##### zu werden.

##### Eine andere wichtige Optimierung ist die nachträgliche Umsortierung. Um die

##### besten Ergebnisse zu erzielen, habe ich sie in 2 Phasen unterteilt. In Phase 1

##### werden aus jedem Cluster die entferntesten Emojis eliminiert, bis in jedem

##### Cluster genau N (ich habe 15 gewählt) eng verbundene Emojis erhalten

##### bleiben, worauf die Einsortierung mit diesen Emojis als Startclustern von vorn

##### beginnen kann. Die 2. Phase ist der Feinschliff. Hier werden von jedem Cluster

##### die N (ich habe 12 gewählt) entferntesten Emojis eliminiert und neu einsortiert,

##### bis sich am Ende nichts mehr an den Clustern ändert.

### 3. Ergebnis

#### bei 🤔, ♀, 🌸, 🐾, 🍰, 🎧, 🚨, 🏆, 🎥, 👉 als Start.

##### Cluster 1: 😂🤔🙄🤣😩😢😡😒!!😖😱😔😳💀😦😟😅😧😠😤😐😑🙃😣💔😞🙁😬😷

😭🤧🤢😪😫😨😁😓😶😥😉😵😏😆😕☹🙂🤕🤒🗿🤨🤡🤮😲🤥😄👺🤬😯🤭👿😴™
😰💩😀🤪🗣😮😃🧐😝🤯😜🚮🤐®🤓😌✉⚰🤫😛🤠😹!?👹😇🐀🐐👌🤲👏🤝

##### Cluster 2: 🏻♀🏽🏼🏾♂👩👨👱⚕🏫🔬👧👵🤸🧘🚶💆🙅👦🎓💁⛹🧚💇🏋🧜👮

🏃💼🏊🙇🙋👴⚖🏄🕵🙆🤰🏌👶👸🤛💃🕺💅🤜🤴🤳🤚✊🤟👯🖕✌🤙✋🖖🤞👋✍
👎👼👊👐☝✂🖐✝🧠🤦🤷🙏

##### Cluster 3: 💖✨🌸🌻🌷🌼💝💕💞🌹🏔💗💛💘💓💐🌺💜🌈💚💟🥀💙🌳🌱❣🍀🌿🧡

💫🏵☮🍃🖤🌾💌🌎🐞🦋💮🎀🕷🚴⭐🍂🌙🕸🌞🍸💋🍄🍁🌅🍒🌜🍯🌛🌌☠🌲☘🕊
🌠🐝⛓🔪🦇🐤🐦🗡🌴🌏🌄♥🚬🏹🌵🌃🌝🌍☺🌐🌚⚔🐲🎃🕶💤👄☄🐉🕯🔮💧🌪
🐚💠🍼🏰💭🗝👠🏳🕕🗺➖

##### Cluster 4: 🌕🌗🌖🌔🌑🌒🌘🌓🐶🐰🐾🐯🐭🐱🐥🐹🐻🐨🐮😻🐑🐵🐧😽🐢🐩🐈😸🐕

🦎😘🐷🐓❤🦖🐒🦊🐘🐅🦄🐴🐔🐛🐣😊🦁🐺🐼🐜🐇🤗🦆🦉😺😗😍🐿😚🐗🐏🐸🐎
🦅👰💍💏👭🙀😿🦍👬⛰🤤👙🔘🚿


##### Cluster 5: 👀👅🍔🍝🍕🍣🍰🍟🍩🍢🍫🍜🍲🌭🍉🍧🍐🍗🍡🍦🍓🐡🍨🍎🍭🥓🍞🍪🍳

🍌🥗🍬🍈🍅🍏🌮🍍🦀🥑🐠🧀🍥🍊🍑🐬🐟🍋🥞🔛🐳🐋🌽☕🏙🏡🏠🐙🍆🥕😋🏘🍿
🐌🥛🙈🐊🍵🌶🥚🍴🙉👖👔🙊🦈👗👕🐍🎪💄💊

##### Cluster 6: 🎶🎵🎉🎺🎤🎼🎸🎻🎹🎇🛬🎷🛫🎧🎊🎁✈🥁🌟🎆🎂📻🎙🅱🛍📈📊📉🎭

😎👑🎅🔊🛰📲🎄🅰🅿🎩📢⚜🤘〽🗽🛡📩👂👽💡🙌

##### Cluster 7:

🔥🚨🚗🚙🚑🚕🚓🚒🚚🔔🚦🚌🏍⚠🚔🚧💨🚲⚡💬🏁🕙🕑🔁↘📦👍🎱🚀👇🔙↗🏎
🔄🔒📣📨🗳🖼🎨⏳🌋▫🆘⬆☑🔝📌🔃🚂🔰👫⛽🔍🔂😙☎🔎🚘🔜▪🛎💉🛸🔌🖌
🔟👆

##### Cluster 8: 🏆⚽❄☀📍🥇🏟🔴🌥🆚🏀🌤⛅🎾⏰🔸🔵⚪🥅📆🏈📅⛄🥈🥉🔹🏐⛳🌨

⛷🗓🎟⏱⚫🔆☃❗🎫🔶🏂🏒🔋🏉⚾🔷🎗🥊🌊⌚🏅🌧✳🕒⌛🌬💪🏖❓⛸☔🏴🏏
🔅👟🏝☁⛵🗨⚓⛈☂🎣⚒🌀🏇

##### Cluster 9:

📼💥⏬🔞🎮💎💰⬇🎥🖥💻💯🔽🕰🎬➡🎞▶📋💦🆒📺💣⏯📎📷⏩💸📽⬅🕹💵💳
📹📸♨😈📀⏪📚📝◀🔫💿📱📖✏🔚🅾🎒🆕🔓🔻⤵🚫💲💷🖨🤩🤑👻🔐🎰📰➕🔺
🤖🔨📡🧢👾💢ℹ©😼🔑🎳❕👁🖊🎯👓

##### Cluster 10:

##### 👉📞🚖💒🛌🍷🥂🍽💑🏨🎈🍇✔🌆🍺✅♣🍻🍹♠↪🥃👈↩♦♻🍾

##### ❌🆓👥✴🆙⭕🎲🆗👤🔱🔗⛔🚩🛑👣🕐🥤✖

##### Die Emojis innerhalb eines Clusters sind nach ihrer durchschnittlichen Distanz

##### sortiert.


