import io
import uvicorn
from app.gpt_dfs import create_dfs_ordered_df
from app.ea_order import order_df_with_elevation_difference
from app.optimizer import optimize_pipe_ids
import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
from app.log_websocket import log_socket_route, websocket_manager


app = FastAPI()
app.include_router(log_socket_route)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IOP = [96.8, 111.6, 125, 142.8, 160.8, 178.6, 201, 223.4, 250.4, 314.8, 366, 416.4, 466.8, 518, 619.6, 700, 800, 900,
       1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500]

@app.get("/download-sample-excel", tags=["PIPE ID OPTIMIZER"])
async def download_sample_excel():
    file_path = "app/sample.xlsx"  # Path to your existing Excel file

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="sample.xlsx"  # This sets the download filename
    )


@app.post("/optimize", tags=["PIPE ID OPTIMIZER"])
async def start_optimization(iop_list: str = None, min_vel:float=0.6, max_vel:float=3,
                             min_pipe_rhae:float=0, min_village_rhae:float=28, xl_file: UploadFile = File(...)):

    print(".....iop list before", iop_list)
    log_message = (f"Starting optimization of {xl_file.filename}, With following inputs:-\n"
                   f"Minimum Velocity: {min_vel}\nMaximum Velocity: {max_vel}\nPipe RHAE: {min_pipe_rhae}\n"
                   f"Village RHAE: {min_village_rhae}\nPipe Dias: {iop_list}")
    await websocket_manager.broadcast(message=log_message)
    print(".....iop list after", iop_list)
    if iop_list is None:
        iop_list = IOP
    else:
        iop_list_of_strings = iop_list.split(',')
        iop_list = [float(iop_s) for iop_s in iop_list_of_strings]
    print(".iop sliadk fkdlist after", iop_list)

    xl_contents = await xl_file.read()

    input_df = pd.read_excel(io.BytesIO(xl_contents), sheet_name="Sheet1")

    log_message = " 1.Sorting with Depth First Search Algorithm....."
    await websocket_manager.broadcast(message=log_message)

    dfs_df = await create_dfs_ordered_df(input_df)

    log_message = " 2. Sorting with Elevation difference......."
    await websocket_manager.broadcast(message=log_message)

    ea_ordered_df = await order_df_with_elevation_difference(dfs_df)

    log_message = " 3. Optimization Starts......."
    await websocket_manager.broadcast(message=log_message)

    processed_df = await optimize_pipe_ids(ordered_df=ea_ordered_df, min_vel=min_vel, max_vel=max_vel,
                            min_pipe_rhae=min_pipe_rhae, min_village_rhae=min_village_rhae, iop_list=iop_list)

    log_message = " 4. Optimization Done.......Sending the Output..."
    await websocket_manager.broadcast(message=log_message)
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        processed_df.to_excel(tmp.name, index=False, engine='openpyxl')

        return FileResponse(
            tmp.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="processed_" + xl_file.filename
        )


handler = Mangum(app)
if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True, port=9000)

# import asyncio
# asyncio.run(start_optimization(
#     min_vel=0.6,
#     max_vel=3,
#     min_pipe_rhae=0,
#     min_village_rhae=28,
#     iop_list=[96.8, 111.6, 125, 142.8, 160.8, 178.6, 201, 223.4, 250.4, 314.8, 366, 416.4, 466.8, 518, 619.6, 700, 800, 900,
#        1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500]
# ))