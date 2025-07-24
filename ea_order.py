

def give_parent_pipe(child_start_node, df_sorted):
    matches = df_sorted.loc[df_sorted['end_node'] == child_start_node]

    if not matches.empty:
        parent_pipe_match = matches.iloc[0].to_dict()

        parent_pipe_match["index"] = int(matches.index[0])

        return parent_pipe_match
    else:

        return None


async def order_df_with_elevation_difference(dfs_df):
    rgrls = dfs_df['ground_level_start'].iat[0]
    print(f".............rgrls{int(rgrls)}", type(int(rgrls)))


    dfs_df['elevation_difference'] = rgrls - dfs_df['ground_level_end'].where(
        dfs_df['end_node'].str.contains("V", regex=False),
        other=None
    )

    df_sorted = dfs_df.sort_values(by="elevation_difference",
                                   ascending=True,
                                   na_position='last')

    child_node_parent_list_dict = {}
    for i, pipe_row in df_sorted.iterrows():
        print("..........i--EAEAEAEA--->", i)

        parent_pipe_dict = give_parent_pipe(pipe_row['start_node'], df_sorted)

        parent_index = None if parent_pipe_dict is None else parent_pipe_dict['index']

        parents_index_list = [i]
        while parent_pipe_dict is not None:
            parents_index_list.append(parent_index)

            parent_pipe_dict = give_parent_pipe(parent_pipe_dict['start_node'], df_sorted)

            parent_index = None if parent_pipe_dict is None else parent_pipe_dict['index']
        child_node_parent_list_dict[pipe_row['end_node']] = parents_index_list


    # with open('cpil.json', 'w') as cpil_json:
    #     json.dump(child_node_parent_list_dict, cpil_json, indent=4)

    ordered_index_list = []

    for end_node, parent_list in child_node_parent_list_dict.items():
        parent_list.sort()
        for index in parent_list:
            if index not in ordered_index_list:
                ordered_index_list.append(index)


    ea_order_df = df_sorted.loc[ordered_index_list]

    ea_order_df = ea_order_df.reset_index(drop=True)

    ea_order_df.to_excel("ea_order.xlsx")

    ea_order_df = ea_order_df.drop(['elevation_difference'], axis=1)

    return ea_order_df