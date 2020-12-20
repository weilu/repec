from queue import PriorityQueue
import pandas as pd
from whoswho import who
from tqdm import tqdm
from itertools import count

repec_authors = pd.read_csv('csv/authors.csv')
top50_authors = pd.read_csv('csv/top50.csv')


tiebreaker = count()
match_results = []
for index, row in tqdm(top50_authors.iterrows(), total=top50_authors.shape[0]):
    name = row['Name']
    sorted_matches = PriorityQueue()
    for i, r in tqdm(repec_authors.iterrows(), total=repec_authors.shape[0]):
        repec_name = r['author_name']
        score = who.ratio(name, repec_name, 'strict')
        # print(score, r)
        repect_author = {'score': score}
        repect_author.update(r.to_dict())
        sorted_matches.put((-score, next(tiebreaker), repect_author))
    match_result = row.to_dict()
    for i in range(1, 4):
        match = sorted_matches.get()[-1]
        for key in match.keys():
            match_result[f'match_{i}_{key}'] = match[key]
    match_results.append(match_result)

df = pd.DataFrame(match_results)
df.to_csv('csv/top50_matched.csv', index=False)
