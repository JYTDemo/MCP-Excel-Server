import pandas as pd
from fastapi import FastAPI
import uvicorn
import os
from pydantic import BaseModel
from typing import Optional
from fastapi_mcp import FastApiMCP

app = FastAPI()

class Item(BaseModel):
    file_name: str
    sheet_name: Optional[str]
    query: Optional[str]


@app.get("/get_files", operation_id="get_files")
def get_files():
    """Endpoint to return a list of files in the current directory."""
    files = os.listdir('./data')
    return {"message": files}


@app.post("/get_sheet_names",operation_id="get_sheet_names")
def get_sheet_names(p_body: Item):
    """Endpoint to return a list of sheet names in an Excel file. Requires the file_name.
    Args : 
        p_body.file_name (Item): Contains the file_name of the Excel file.
    
    """
    excel_file_path = f'./data/{p_body.file_name}'  # Update with your Excel file path
    if not os.path.exists(excel_file_path): 
        return {"message": "Excel file not found."}   
    excel_file = pd.ExcelFile(excel_file_path)
    sheet_names = excel_file.sheet_names
    return {"message": sheet_names}


@app.post("/get_sheet_metadata",operation_id="get_sheet_metadata")
def get_sheet_metadata(p_body: Item):
    """Endpoint to return metadata of sheets in an Excel file. Requires the file_name and sheet_name.
    
    Args : 
        p_body.file_name (Item): Contains the file_name and sheet_name of the Excel file.
        p_body.sheet_name (Item): Contains the sheet_name of the Excel file.
    """
    excel_file_path = f'./data/{p_body.file_name}'  # Update with your Excel file path
    if not os.path.exists(excel_file_path): 
        return {"message": "Excel file not found."} 
    df = pd.read_excel(excel_file_path, sheet_name=p_body.sheet_name)
    metadata = df.columns
    return {"message": list(metadata)}


@app.post("/analyse_data",operation_id="analyse_data")
def analyse_data(p_body: Item):
    """Endpoint to query data from a specific sheet in an Excel file. Requires the file_name, sheet_name, 
    and code snippet to be executed on df as query and the final result to be stored in a string variable x.
    Args : 
        p_body.file_name (Item): Contains the file_name and sheet_name of the Excel file
        p_body.sheet_name (Item): Contains the sheet_name of the Excel file.
        p_body.query (Item): Contains the code snippet to be executed on df.
    Example query: "x = df['column_name'].mean()"
    """
    print(p_body.query)
    excel_file_path = f'./data/{p_body.file_name}'  # Update with your Excel file path
    if not os.path.exists(excel_file_path): 
        return {"message": "Excel file not found."} 
    df = pd.read_excel(excel_file_path, sheet_name=p_body.sheet_name)
    local_vars = {"df": df}
    exec(p_body.query,{}, local_vars)   
    x = local_vars.get("x", "") 
    # df_string  = df.to_string()
    print(x)
    return {"message": x}


mcp = FastApiMCP(app,
                include_operations=["get_files", "get_sheet_names", "get_sheet_metadata", "analyse_data"])
mcp.mount()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8502)