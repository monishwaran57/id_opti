# from gpt_dfs import dfs_df as ordered_df
# from new_order import new_order_df as ordered_df
# from new_order import deepest_branch_df as ordered_df, deepest_branch_indices
from opti_classes import (Pipe, max_vel, forget_gap,
                          min_vel, min_pipe_rhae, min_village_rhae)
from typing import Dict
import pandas as pd

ordered_df = pd.read_excel("deep_branch.xlsx", index_col=0)
ordered_df = ordered_df.drop(["new_iop","new_velocity","new_fhl","available_residual_head_at_start","residual_head_at_end"], axis=1)
deepest_branch_indices = ordered_df.index.to_list()

def give_parent_pipe_details(child_start_node):
    matches = ordered_df.loc[ordered_df['end_node'] == child_start_node]

    if not matches.empty:
        parent_pipe_match = matches.iloc[0].to_dict()

        parent_pipe_match["index"] = int(matches.index[0])

        return parent_pipe_match
    else:

        return None

def check_velocity(pipe):
    if min_vel <= pipe.velocity <= max_vel:
        return True
    else:
        return False

def check_rhae(pipe):
    min_rhae = min_village_rhae if pipe.is_village_endpoint else min_pipe_rhae
    if pipe.rhae >= min_rhae:
        return True
    else:
        return False


def create_pidx_and_piop_dict(pipe):
    pidx_and_piop = {}
    pp_index = pipe.parent_pipe_index
    while pp_index is not None:
        p_pipe = calculated_dict[pp_index]
        pidx_and_piop[p_pipe.index] = p_pipe.iop
        pp_index = p_pipe.parent_pipe_index
    return pidx_and_piop


def recalculate_rhae_for_childs(p_pipe):
    while p_pipe.is_village_endpoint:
        if p_pipe.index + 1 in calculated_dict:
            p_pipe = calculated_dict[p_pipe.index+1]
        else:
            return True
    parent_index_in_deepest_branch_list = deepest_branch_indices.index(p_pipe.index)
    child_index = deepest_branch_indices[parent_index_in_deepest_branch_list+1]
    if child_index in calculated_dict:
        child_pipe = calculated_dict[child_index]

        child_pipe.parent_iop = p_pipe.iop
        child_pipe.rhas = p_pipe.rhae
        child_pipe.rhae = child_pipe.find_rhae()
        calculated_dict[child_pipe.index] = child_pipe
        recalculate_rhae_for_childs(child_pipe)
    else:
        pass


def need_to_increase_parent_iop(pipe):
    pidx_and_piop_dict = create_pidx_and_piop_dict(pipe)

    iop_indices_dict = {}
    for idx, iop in pidx_and_piop_dict.items():
        iop_indices_dict[iop] = [idx2 for idx2, iop2 in pidx_and_piop_dict.items() if iop == iop2]

    if len(iop_indices_dict) != 0:
        least_iop_among_parents = min(iop_indices_dict)
        top_parent_index_to_be_increased = min(iop_indices_dict[least_iop_among_parents])
    else:
        top_parent_index_to_be_increased = 0

    p_pipe = calculated_dict[top_parent_index_to_be_increased]

    iop_increased_p_pipe = rhae_low_increase_iop(p_pipe)

    child_started_the_loop_index_in = child_pipe_loop_list[0]
    if (child_started_the_loop_index_in - iop_increased_p_pipe.index) >= forget_gap:
        return iop_increased_p_pipe

    calculated_dict[iop_increased_p_pipe.index] = iop_increased_p_pipe

    recalculate_rhae_for_childs(iop_increased_p_pipe)

    pipe.parent_iop = iop_increased_p_pipe.iop
    pipe.rhas = calculated_dict[pipe.parent_pipe_index].rhae
    pipe.rhae = pipe.find_rhae()

    if check_velocity(pipe):
        if check_rhae(pipe):
            return pipe
        else:
            pipe = rhae_low_increase_iop(pipe=pipe)
            return pipe
    else:
        raise ValueError("ennanga velocity pathala")


def rhae_low_increase_iop(pipe):
    if pipe.index not in child_pipe_loop_list:
        child_pipe_loop_list.append(pipe.index)
    current_iop_index = pipe.allowed_iops.index(pipe.iop)
    increased_iop_index = current_iop_index + 1
    while increased_iop_index < len(pipe.allowed_iops):
        increased_iop = pipe.allowed_iops[increased_iop_index]
        if increased_iop <= pipe.parent_iop:
            pipe.iop = increased_iop
            pipe.velocity = pipe.find_velocity()
            if check_velocity(pipe):
                pipe.fhl = pipe.find_fhl()
                pipe.rhae = pipe.find_rhae()
                if check_rhae(pipe):
                    return pipe
                else:
                    increased_iop_index += 1
            else:
                raise ValueError("Rhae pathalannu velocity increase panna, velocity criteria break aagudhu!!!!")
        else:
            pipe = need_to_increase_parent_iop(pipe)
            return pipe
    else:
        pipe = need_to_increase_parent_iop(pipe)
        return pipe

parent_indices_list = ordered_df[~ordered_df['end_node'].str.contains('V')].index.tolist()

child_pipe_loop_list = []

calculated_dict:Dict[int, Pipe] = {}

i=len(calculated_dict)

leng_of_order_df = len(ordered_df)

while i < len(ordered_df):
    print("---->", i)
    if i == 52:
        print("asterdam")

    pipe_from_df = ordered_df.loc[deepest_branch_indices[i]]

    parent_pipe = give_parent_pipe_details(child_start_node=pipe_from_df['start_node'])

    parent_pipe_index = None if parent_pipe is None else parent_pipe['index']

    rhas = 0 if parent_pipe is None else calculated_dict[parent_pipe_index].rhae

    del pipe_from_df['old_iop']

    current_pipe = Pipe(**pipe_from_df, rhas=rhas, index=deepest_branch_indices[i])

    current_pipe.parent_iop = current_pipe.allowed_iops[-1] if parent_pipe is None else calculated_dict[parent_pipe_index].iop

    current_pipe.parent_pipe_index = None if parent_pipe is None else parent_pipe_index

    if check_rhae(current_pipe):
        calculated_dict[deepest_branch_indices[i]] = current_pipe
        i = len(calculated_dict)
    else:
        current_pipe = rhae_low_increase_iop(current_pipe)
        child_started_the_loop_index = child_pipe_loop_list[0]
        if (child_started_the_loop_index - current_pipe.index) >= forget_gap:
            child_indices_to_be_forgotten_list = [idx for idx in calculated_dict if idx > current_pipe.index]
            for idx in child_indices_to_be_forgotten_list:
                del calculated_dict[idx]

            calculated_dict[current_pipe.index] = current_pipe
            i = len(calculated_dict)
            child_pipe_loop_list = []
        else:
            calculated_dict[deepest_branch_indices[i]] = current_pipe
            i = len(calculated_dict)
            child_pipe_loop_list = []


for key, value in calculated_dict.items():
    ordered_df.loc[key, 'new_iop'] = value.iop
    ordered_df.loc[key, 'new_velocity'] = value.velocity
    ordered_df.loc[key, 'new_fhl'] = value.fhl
    ordered_df.loc[key, 'available_residual_head_at_start'] = value.rhas
    ordered_df.loc[key, 'residual_head_at_end'] = value.rhae
    ordered_df.loc[key, 'allowed_iops'] = str(value.allowed_iops)

ordered_df.to_excel("deep_opti.xlsx")