# from gpt_dfs import dfs_df as ordered_df
# from new_order import new_order_df as ordered_df
# from ea_order import ea_order_df as ea_ordered_df
# from opti_classes import (Pipe, max_vel, forget_gap,
#                           min_vel, min_pipe_rhae, min_village_rhae)
from opti_classes import (Pipe)
from typing import Dict
import pandas as pd



def give_parent_pipe_details(child_start_node, ordered_df):
    matches = ordered_df.loc[ordered_df['end_node'] == child_start_node]

    if not matches.empty:
        parent_pipe_match = matches.iloc[0].to_dict()

        parent_pipe_match["index"] = int(matches.index[0])

        return parent_pipe_match
    else:

        return None

def check_velocity(pipe, min_vel, max_vel):
    if min_vel <= pipe.velocity <= max_vel:
        return True
    else:
        return False

def check_rhae(pipe, min_village_rhae, min_pipe_rhae):
    min_rhae = min_village_rhae if pipe.is_village_endpoint else min_pipe_rhae
    if pipe.rhae >= min_rhae:
        return True
    else:
        return False


def create_pidx_and_piop_dict(pipe, calculated_dict):
    pidx_and_piop = {}
    pp_index = pipe.parent_pipe_index
    while pp_index is not None:
        p_pipe = calculated_dict[pp_index]
        pidx_and_piop[p_pipe.index] = p_pipe.iop
        pp_index = p_pipe.parent_pipe_index
    return pidx_and_piop

def create_current_max_iop_dict_of_parents(pipe, calculated_dict):
    current_max_iop_dict_of_parents = {}
    pp_index = pipe.parent_pipe_index
    while pp_index is not None:
        p_pipe = calculated_dict[pp_index]
        current_max_iop_dict_of_parents[pp_index] = {
            "current_iop": p_pipe.iop,
            "max_iop": p_pipe.allowed_iops[-1]}
        pp_index = p_pipe.parent_pipe_index
    return current_max_iop_dict_of_parents

def get_child_pipes(parent_end_node, ordered_df):
    # Find all pipes where start_node matches parent's end_node
    child_pipes = ordered_df[ordered_df['start_node'] == parent_end_node]

    return child_pipes.to_dict(orient="index")


def recalculate_rhae_for_childs(p_pipe, calculated_dict, ordered_df):
    childs = get_child_pipes(p_pipe.end_node, ordered_df=ordered_df)
    for child_index, child_dict in childs.items():
        if child_index in calculated_dict:
            child_pipe = calculated_dict[child_index]

            child_pipe.parent_iop = p_pipe.iop
            child_pipe.rhas = p_pipe.rhae
            child_pipe.rhae = child_pipe.find_rhae()
            calculated_dict[child_pipe.index] = child_pipe
            recalculate_rhae_for_childs(child_pipe, calculated_dict, ordered_df)
        else:
            pass


def need_to_increase_parent_iop(pipe, calculated_dict, ordered_df, min_vel, max_vel, min_pipe_rhae, min_village_rhae):
    pidx_and_piop_dict = create_pidx_and_piop_dict(pipe, calculated_dict)

    iop_indices_dict = {}
    for idx, iop in pidx_and_piop_dict.items():
        iop_indices_dict[iop] = [idx2 for idx2, iop2 in pidx_and_piop_dict.items() if iop == iop2]

    if len(iop_indices_dict) != 0:
        least_iop_among_parents = min(iop_indices_dict)
        top_parent_index_to_be_increased = min(iop_indices_dict[least_iop_among_parents])
    else:
        top_parent_index_to_be_increased = 0

    p_pipe = calculated_dict[top_parent_index_to_be_increased]

    iop_increased_p_pipe = rhae_low_increase_iop(p_pipe, calculated_dict, ordered_df
                                                 , min_vel=min_vel, max_vel=max_vel,
                                                 min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae
                                                 )


    calculated_dict[iop_increased_p_pipe.index] = iop_increased_p_pipe

    recalculate_rhae_for_childs(iop_increased_p_pipe, calculated_dict, ordered_df)

    pipe.parent_iop = iop_increased_p_pipe.iop
    pipe.rhas = calculated_dict[pipe.parent_pipe_index].rhae
    pipe.rhae = pipe.find_rhae()

    if check_velocity(pipe, min_vel=min_vel, max_vel=max_vel):
        if check_rhae(pipe, min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae):
            return pipe
        else:
            pipe = rhae_low_increase_iop(pipe=pipe, calculated_dict=calculated_dict,
                                         ordered_df=ordered_df, min_vel=min_vel, max_vel=max_vel,
                                               min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae)
            return pipe
    else:
        raise ValueError("ennanga velocity pathala")


def rhae_low_increase_iop(pipe, calculated_dict, ordered_df, min_vel, max_vel, min_pipe_rhae, min_village_rhae):
    if pipe.index == len(calculated_dict):
        parrent_current_max_iop = create_current_max_iop_dict_of_parents(pipe, calculated_dict)
        is_every_parent_at_max_iop = True
        for pp_index, current_max_iop_dict in parrent_current_max_iop.items():
            if current_max_iop_dict["current_iop"] != current_max_iop_dict["max_iop"]:
                is_every_parent_at_max_iop = False
                break
        if is_every_parent_at_max_iop:
            return pipe

    current_iop_index = pipe.allowed_iops.index(pipe.iop)
    increased_iop_index = current_iop_index + 1
    while increased_iop_index < len(pipe.allowed_iops):
        increased_iop = pipe.allowed_iops[increased_iop_index]
        if increased_iop <= pipe.parent_iop:
            pipe.iop = increased_iop
            pipe.velocity = pipe.find_velocity()
            if check_velocity(pipe, min_vel=min_vel, max_vel=max_vel):
                pipe.fhl = pipe.find_fhl()
                pipe.rhae = pipe.find_rhae()
                if check_rhae(pipe, min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae):
                    return pipe
                else:
                    increased_iop_index += 1
            else:
                raise ValueError("Rhae pathalannu velocity increase panna, velocity criteria break aagudhu!!!!")
        else:
            pipe = need_to_increase_parent_iop(pipe, calculated_dict, ordered_df, min_vel=min_vel, max_vel=max_vel,
                                               min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae)
            return pipe
    else:
        pipe = need_to_increase_parent_iop(pipe, calculated_dict, ordered_df, min_vel=min_vel, max_vel=max_vel,
                                               min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae)
        return pipe

# parent_indices_list = ordered_df[~ordered_df['end_node'].str.contains('V')].index.tolist()




async  def optimize_pipe_ids(ordered_df, min_vel, max_vel, min_pipe_rhae, min_village_rhae, iop_list):
    calculated_dict: Dict[int, Pipe] = {}

    i = len(calculated_dict)

    leng_of_order_df = len(ordered_df)

    while i < len(ordered_df):
        print("---->", i)
        if i == 52:
            print("asterdam")

        pipe_from_df = ordered_df.loc[i]

        parent_pipe = give_parent_pipe_details(child_start_node=pipe_from_df['start_node'], ordered_df=ordered_df)

        parent_pipe_index = None if parent_pipe is None else parent_pipe['index']

        rhas = 0 if parent_pipe is None else calculated_dict[parent_pipe_index].rhae

        del pipe_from_df['old_iop']

        current_pipe = Pipe(**pipe_from_df, rhas=rhas, index=i, min_vel=min_vel, max_vel=max_vel, iop_list=iop_list)

        current_pipe.parent_iop = current_pipe.allowed_iops[-1] if parent_pipe is None else calculated_dict[parent_pipe_index].iop

        current_pipe.parent_pipe_index = None if parent_pipe is None else parent_pipe_index

        if check_rhae(current_pipe, min_village_rhae, min_pipe_rhae):
            calculated_dict[i] = current_pipe
            i = len(calculated_dict)
        else:
            current_pipe = rhae_low_increase_iop(current_pipe, calculated_dict, ordered_df, min_vel=min_vel, max_vel=max_vel,
                                               min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae)
            calculated_dict[i] = current_pipe
            i = len(calculated_dict)


    for key, value in calculated_dict.items():
        ordered_df.loc[key, 'new_iop'] = value.iop
        ordered_df.loc[key, 'new_velocity'] = value.velocity
        ordered_df.loc[key, 'new_fhl'] = value.fhl
        ordered_df.loc[key, 'available_residual_head_at_start'] = value.rhas
        ordered_df.loc[key, 'residual_head_at_end'] = value.rhae
        ordered_df.loc[key, 'allowed_iops'] = str(value.allowed_iops)

    ordered_df.to_excel("opti.xlsx")

    return ordered_df

# import asyncio
# asyncio.run(optimize_pipe_ids(ea_ordered_df))
# with pd.ExcelWriter('optiformulas.xlsx', engine='xlsxwriter') as writer:
#     ordered_df.to_excel(writer, sheet_name='Sheet1')
#
#     # Get workbook and worksheet objects
#     workbook = writer.book
#     worksheet = writer.sheets['Sheet1']
#
#     # Add formulas
#     worksheet.write_formula('J2', '=ROUNDDOWN(D2 * (4 / (PI() * (I2 / 1000) ^ 2)), 2)')
#     worksheet.write_formula('K2', '=ROUNDDOWN(((E2 * (D2 / 1) ^1.81) / (994.62 * (I2 / 1000) ^ 4.81)) * 1.1, 2)')
#     worksheet.write_formula('L2', '=IF(COUNTIF(C$2:C2, B2)=0, 0, INDEX(M$2:M2, MATCH(B2, C$2:C2, 0)))')
#     worksheet.write_formula('M2', '=ROUNDDOWN((F2-G2 + L2) - K2, 2)')
