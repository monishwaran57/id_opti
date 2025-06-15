from gpt_dfs import dfs_df as ordered_df
from opti_classes import (Pipe, max_vel,
                          min_vel, min_pipe_rhae, min_village_rhae)
from typing import Dict


def give_parent_pipe_details(child_start_node):
    matches = ordered_df.loc[ordered_df['end_node'] == child_start_node]

    if not matches.empty:
        parent_pipe_match = matches.iloc[0].to_dict()

        parent_pipe_match["index"] = matches.index[0]

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




def need_to_increase_parent_iop(pipe):
    pidx_and_piop_dict = create_pidx_and_piop_dict(pipe)

    iop_indices_dict = {}
    for idx, iop in pidx_and_piop_dict.items():
        iop_indices_dict[iop] = [idx2 for idx2, iop2 in pidx_and_piop_dict.items() if iop == iop2]
    print("..iop_indices_dict", iop_indices_dict)


def rhae_low_increase_iop(pipe):
    print("criteria unsatisfied pipe", pipe.__dict__)
    current_iop_index = pipe.allowed_iops.index(pipe.iop)
    if current_iop_index+1 < len(pipe.allowed_iops):
        increased_iop = pipe.allowed_iops[current_iop_index+1]
        if increased_iop <= pipe.parent_iop:
            pipe.iop = increased_iop
            pipe.velocity = pipe.find_velocity()
            if check_velocity(pipe):
                pipe.fhl = pipe.find_fhl()
                pipe.rhae = pipe.find_rhae()
                if check_rhae(pipe):
                    return pipe
                else:
                    pipe = rhae_low_increase_iop(pipe)
                    return pipe
            else:
                raise ValueError("Rhae pathalannu velocity increase panna, velocity criteria break aagudhu!!!!")
        else:
            print("pen endra jadhiyilae aayirathil aval oruthi")
    else:
        print("pon vairam koduthalum, pothathamma seer senathi")
        need_to_increase_parent_iop(pipe)


calculated_dict:Dict[int, Pipe] = {}

i=len(calculated_dict)

while i < len(ordered_df):
    pipe_from_df = ordered_df.loc[i]

    parent_pipe = give_parent_pipe_details(child_start_node=pipe_from_df['start_node'])

    parent_pipe_index = None if parent_pipe is None else parent_pipe['index']

    rhas = 0 if parent_pipe is None else calculated_dict[parent_pipe_index].rhae

    del pipe_from_df['old_iop']

    current_pipe = Pipe(**pipe_from_df, rhas=rhas, index=i)

    current_pipe.parent_iop = current_pipe.allowed_iops[-1] if parent_pipe is None else calculated_dict[parent_pipe_index].iop

    current_pipe.parent_pipe_index = None if parent_pipe is None else parent_pipe_index

    if check_rhae(current_pipe):
        calculated_dict[i] = current_pipe
        i = len(calculated_dict)
    else:
        current_pipe = rhae_low_increase_iop(current_pipe)
        calculated_dict[i] = current_pipe
        i = len(calculated_dict)
        break

