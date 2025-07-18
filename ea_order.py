from gpt_dfs import dfs_df

rgrls = dfs_df['ground_level_start'].iat[0]
print(f".............rgrls{int(rgrls)}", type(int(rgrls)))


dfs_df['elevation_difference'] = rgrls - dfs_df['ground_level_end'].where(
    dfs_df['end_node'].str.contains("V", regex=False),
    other=None
)
dfs_df.to_excel("ed.xlsx")

df_sorted = dfs_df.sort_values(by="elevation_difference",
                               ascending=True,
                               na_position='last')

df_sorted.to_excel("eatest.xlsx")

for i, pipe_row in df_sorted.iterrows():
    print("start")