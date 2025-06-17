from gpt_dfs import dfs_df as ordered_df
from formulas import IOP, find_closest_iop_index_by_formula, find_velocity_by_formula, find_friction_head_loss_by_formula, find_residual_head_at_end_by_formula


def give_parent_pipe_details(child_start_node):
    matches = ordered_df.loc[ordered_df['end_node'] == child_start_node]

    if not matches.empty:
        parent_pipe = matches.iloc[0].to_dict()

        parent_pipe["index"] = matches.index[0]

        return parent_pipe
    else:

        return None

def add_parent_pipe_index_to_the_list(child_pipe, end_node):
    parent_pipe = give_parent_pipe_details(child_pipe['start_node'])

    if parent_pipe is not None:
        asce_calci_dict[end_node].append(int(parent_pipe['index']))

        add_parent_pipe_index_to_the_list(parent_pipe, end_node)

calci_dict = {}

for i, row in ordered_df.iterrows():
    print(".........", i)
    if i == 1237:
        print("...")
    parent_pipe_index_list = ordered_df.index[ordered_df['end_node'] == row['start_node']].to_list()

    parent_pipe_index = None if len(parent_pipe_index_list) == 0 else parent_pipe_index_list[0]

    PARENT_IOP = None if parent_pipe_index is None else calci_dict[parent_pipe_index]['iop']

    RHAS = 0 if parent_pipe_index is None else calci_dict[parent_pipe_index]['rhae']

    closest_iop_index = find_closest_iop_index_by_formula(row['discharge'])

    closest_iop = IOP[closest_iop_index]

    velocity = find_velocity_by_formula(discharge=row['discharge'], id_of_pipe=closest_iop)

    if closest_iop_index != 0:
        while velocity < 0.6 or velocity > 3:
            closest_iop = IOP[closest_iop_index + 1]
            velocity = find_velocity_by_formula(discharge=row['discharge'], id_of_pipe=closest_iop)
            if 0.6 <= velocity <= 3:
                break
            else:
                closest_iop_index += 1
        # raise ValueError("velocity goes below 0.6")

    fhl = find_friction_head_loss_by_formula(length=row['length'],
                                             discharge=row['discharge'],
                                             cr_value=1,
                                             iop=closest_iop)

    diff_in_g_level = row['ground_level_start'] - row['ground_level_end']

    rhae = find_residual_head_at_end_by_formula(diff_in_g_level=diff_in_g_level, rhas=RHAS,
                                                fhl=fhl)


    calci_dict[i] = {
        "start_node": row['start_node'],
        "end_node": row['end_node'],
        "length": row['length'],
        "discharge": row['discharge'],
        "ground_level_start": row["ground_level_start"],
        "ground_level_end": row["ground_level_end"],
        "parent_iop": PARENT_IOP,
        "iop": closest_iop,
        "iop_index": IOP.index(closest_iop),
        "fhl": fhl,
        "velocity": velocity,
        "rhas": RHAS,
        "rhae": rhae
    }


for key, value in calci_dict.items():
    ordered_df.loc[key, 'new_iop'] = value['iop']
    ordered_df.loc[key, 'new_velocity'] = value['velocity']
    ordered_df.loc[key, 'new_fhl'] = value['fhl']
    ordered_df.loc[key, 'available_residual_head_at_start'] = round(value['rhas'], 2)
    ordered_df.loc[key, 'residual_head_at_end'] = round(value['rhae'], 2)

asce_ordered_df = ordered_df.sort_values(by="residual_head_at_end")

asce_ordered_df.to_excel('ascendingly_ordered_by_-ve_rhae.xlsx')

asce_calci_dict = {}

ordered_list = []

print("going to start lifting the deepest branch to the top, and others sequentially")
for ridx, pipe in asce_ordered_df.iterrows():
    print("------------()()()", ridx)
    if pipe['end_node'] not in asce_calci_dict:

        asce_calci_dict[pipe['end_node']] = [ridx]


        add_parent_pipe_index_to_the_list(pipe, end_node=pipe['end_node'])




print(asce_calci_dict)

print("now i'm going to reorder the dict")
for end_node, index_list in asce_calci_dict.items():
    index_list.sort()
    for idx in index_list:
        if idx not in ordered_list:
            ordered_list.append(idx)

print("\n", ordered_list)

new_order_df = asce_ordered_df.loc[ordered_list]

new_order_df = new_order_df.reset_index(drop=True)

new_order_df.to_excel("neworder.xlsx")

new_order_df = new_order_df.drop(["old_iop","new_iop","new_velocity","new_fhl","available_residual_head_at_start","residual_head_at_end"], axis=1)