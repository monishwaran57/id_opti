from gpt_dfs import dfs_df as ordered_df
from opti_classes import Pipe
from typing import Dict

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

calci_dict:Dict[int, Pipe] = {}

for i, row in ordered_df.iterrows():
    print(".........", i)

    parent_pipe_index_list = ordered_df.index[ordered_df['end_node'] == row['start_node']].to_list()

    parent_pipe_index = None if len(parent_pipe_index_list) == 0 else parent_pipe_index_list[0]

    PARENT_IOP = None if parent_pipe_index is None else calci_dict[parent_pipe_index].iop

    RHAS = 0 if parent_pipe_index is None else calci_dict[parent_pipe_index].rhae

    del row['old_iop']

    current_pipe = Pipe(**row, rhas=RHAS, index=i)

    current_pipe.parent_iop = current_pipe.allowed_iops[-1] if PARENT_IOP is None else calci_dict[
        parent_pipe_index].iop

    current_pipe.parent_pipe_index = None if parent_pipe_index is None else parent_pipe_index


    calci_dict[i] = current_pipe


for key, value in calci_dict.items():
    ordered_df.loc[key, 'new_iop'] = value.iop
    ordered_df.loc[key, 'new_velocity'] = value.velocity
    ordered_df.loc[key, 'new_fhl'] = value.fhl
    ordered_df.loc[key, 'available_residual_head_at_start'] = value.rhas
    ordered_df.loc[key, 'residual_head_at_end'] = value.rhae

asce_ordered_df = ordered_df.sort_values(by="residual_head_at_end")

# asce_ordered_df.to_excel('ascendingly_ordered_by_-ve_rhae.xlsx')

asce_calci_dict = {}

ordered_list = []

print("going to start lifting the deepest branch to the top, and others sequentially")
for ridx, pipe in asce_ordered_df.iterrows():
    print("------------()()()", ridx)
    if pipe['end_node'] not in asce_calci_dict:

        asce_calci_dict[pipe['end_node']] = [ridx]

        add_parent_pipe_index_to_the_list(pipe, end_node=pipe['end_node'])




# print("enga", asce_calci_dict.keys())
# deepest_child_node = list(asce_calci_dict.keys())[0]
# deepest_branch_indices = asce_calci_dict[deepest_child_node]
# print("....deepest branch indices\n", deepest_branch_indices)
#
# deepest_branch_indices.sort()
# deepest_branch_df = asce_ordered_df.loc[deepest_branch_indices]
# # deepest_branch_df = deepest_branch_df.reset_index(drop=True)
# deepest_branch_df.to_excel("deep_branch.xlsx")
print("now i'm going to reorder the dict")
for end_node, index_list in asce_calci_dict.items():
    index_list.sort()
    for idx in index_list:
        if idx not in ordered_list:
            ordered_list.append(idx)

print("\n---->", ordered_list)

new_order_df = asce_ordered_df.loc[ordered_list]

new_order_df = new_order_df.reset_index(drop=True)

new_order_df.to_excel("neworder.xlsx")

new_order_df = new_order_df.drop(["new_iop","new_velocity","new_fhl","available_residual_head_at_start","residual_head_at_end"], axis=1)