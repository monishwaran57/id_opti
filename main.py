# from gpt_dfs import dfs_df as ordered_df
from new_order import new_order_df as ordered_df
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


def recalculate_rhae_for_childs(p_pipe):
    if p_pipe.index+1 in calculated_dict:
        child_pipe = calculated_dict[p_pipe.index+1]
        if p_pipe.is_village_endpoint:
            raise ValueError("Adhu epdi thimingalam, p_pipe la 'V'")
        child_pipe.parent_iop = p_pipe.iop
        child_pipe.rhas = p_pipe.rhae
        child_pipe.rhae = child_pipe.find_rhae()
        calculated_dict[child_pipe.index] = child_pipe
        recalculate_rhae_for_childs(child_pipe)
    else:
        pass


def need_to_increase_parent_iop(pipe):
    print("rhae needing pipe:::", pipe.__dict__)
    pidx_and_piop_dict = create_pidx_and_piop_dict(pipe)

    iop_indices_dict = {}
    for idx, iop in pidx_and_piop_dict.items():
        iop_indices_dict[iop] = [idx2 for idx2, iop2 in pidx_and_piop_dict.items() if iop == iop2]
    print("..iop_indices_dict", iop_indices_dict)

    least_iop_among_parents = min(iop_indices_dict)


    top_parent_index_to_be_increased = min(iop_indices_dict[least_iop_among_parents])


    print("... top iop to be increased", top_parent_index_to_be_increased)


    p_pipe = calculated_dict[top_parent_index_to_be_increased]


    iop_increased_p_pipe = rhae_low_increase_iop(p_pipe)


    calculated_dict[iop_increased_p_pipe.index] = iop_increased_p_pipe


    recalculate_rhae_for_childs(iop_increased_p_pipe)

    pipe.parent_iop = iop_increased_p_pipe.iop
    pipe.rhas = calculated_dict[pipe.parent_pipe_index].rhae
    pipe.rhae = pipe.find_rhae()
    print("..pipe.rhae", pipe.rhae)


    if check_velocity(pipe):
        if check_rhae(pipe):
            return pipe
        else:
            print("adichaDhu podhum da off panu da")
            pipe = rhae_low_increase_iop(pipe=pipe)
            return pipe
    else:
        print("ellam maarum ellam maarum")
        raise ValueError("ennanga velocity pathala")








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
            pipe = need_to_increase_parent_iop(pipe)
            return pipe
    else:
        print("pon vairam koduthalum, pothathamma seer senathi")
        pipe = need_to_increase_parent_iop(pipe)
        return pipe


calculated_dict:Dict[int, Pipe] = {}

i=len(calculated_dict)

while i < len(ordered_df):
    pipe_from_df = ordered_df.loc[i]

    parent_pipe = give_parent_pipe_details(child_start_node=pipe_from_df['start_node'])

    parent_pipe_index = None if parent_pipe is None else parent_pipe['index']

    rhas = 0 if parent_pipe is None else calculated_dict[parent_pipe_index].rhae

    # del pipe_from_df['old_iop']

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


