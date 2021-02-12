import pandas as pd
import numpy as np

col_name = 'manual_match (match_1, match_2, match_3 or None)'
keep_cols = ['University Name', 'Name', col_name]
all_df = pd.read_csv('csv/top50_matched.csv')
probable_df = pd.read_csv('csv/probable_matches.csv', usecols=keep_cols)
multiple_df = pd.read_csv('csv/multiple_matches.csv', usecols=keep_cols)

manual_df = pd.concat([probable_df, multiple_df])
manual_df.rename(columns={col_name: 'manual_match'}, inplace=True)

df = pd.merge(all_df, manual_df, how='left', on=['University Name', 'Name'])

conditions = [
    (df['manual_match'] == 'match_1'),
    (df['manual_match'] == 'match_2'),
    (df['manual_match'] == 'match_3'),
    (df['manual_match'] == 'None'),
    (df['match_1_score'] == 100),
]
choices = [
    df['match_1_author_id'],
    df['match_2_author_id'],
    df['match_3_author_id'],
    None,
    df['match_1_author_id'],
]
df['repec_author_id'] = np.select(conditions, choices, default=None)
id_count = df.groupby('repec_author_id').size()
duplicate_matches = id_count[id_count > 1].index.to_list()
duplicates = df[df.repec_author_id.isin(duplicate_matches)]
duplicates.to_csv('csv/many_to_one_matches.csv')

df.to_csv('csv/top50_matched_cleaned.csv', index=False)

input_df = pd.read_csv('csv/top50_matched_cleaned.csv', usecols=['repec_author_id'])
author_ids = input_df.dropna().repec_author_id.unique().tolist()
indf = pd.DataFrame({'authorId': author_ids})
indf.to_csv('csv/input.csv', index=False)

