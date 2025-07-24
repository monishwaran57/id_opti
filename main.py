from gpt_dfs import create_dfs_ordered_df
from ea_order import order_df_with_elevation_difference
from optimizer import optimize_pipe_ids
import pandas as pd

async def start_optimization(min_vel, max_vel, min_pipe_rhae, min_village_rhae, iop_list):
    input_df = pd.read_excel('dc2.xlsx', sheet_name="Sheet1")

    dfs_df = await create_dfs_ordered_df(input_df)

    ea_ordered_df = await order_df_with_elevation_difference(dfs_df)

    await optimize_pipe_ids(ordered_df=ea_ordered_df, min_vel=min_vel, max_vel=max_vel,
                            min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae, iop_list=iop_list)



import asyncio
asyncio.run(start_optimization(
    min_vel=0.6,
    max_vel=3,
    min_pipe_rhae=0,
    min_village_rhae=28,
    iop_list=[96.8, 111.6, 125, 142.8, 160.8, 178.6, 201, 223.4, 250.4, 314.8, 366, 416.4, 466.8, 518, 619.6, 700, 800, 900,
       1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500]
))