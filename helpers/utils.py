#########################################################################################
# Filename    : utils.py
# Fi1eType    : Python Source file
# Author      : Rahal Amrith
# Created on  : 13/10/2022
# description : Python Utility Functions for
#########################################################################################

import re
import os
import pandas as pd
import openpyxl

from helpers.htmlreport import buildHtmlReport


def getProfilesFromConfig(path):

    pName = []

    cfgFile = open(path, 'r')
    Lines = cfgFile.readlines()

    for line in Lines:
        m = re.findall(r"\[.*\]", line)
        if len(m) > 0:
            pName.append(str(m[0]).replace('[', "").replace(']', ""))

    return pName


def getAwsConfigs(path):

    configs = {}

    cfgFile = open(path, 'r')
    Lines = cfgFile.readlines()

    currentProfile = ""

    for line in Lines:

        if line == "\n":
            continue

        pName = re.findall(r"\[.*\]", line)

        if len(pName) > 0:
            currentProfile = str(pName[0]).replace('[', "").replace(']', "")
            configs[currentProfile] = {}
            continue

        kvp = re.findall(r"[a-z_-]+=.+", line)

        if len(kvp) > 0:
            key = line.split("=")[0]
            value = line.split("=")[1].replace("\n", "")
            configs[currentProfile][key] = value

            continue

    return configs


def getOCICompartmentName(list, id):
    name = ""

    try:
        name = list[id]['name']
    except:
        name = "Root"

    return name


def searchDictionalyArray(list, search, key):

    index = -1

    for i, item in enumerate(list):
        if item[key] == search:
            index = i
            break

    return index

def mergeCellsInExcellV1(filename, excludeMerge=[]):

    # Load the workbook
    wb = openpyxl.load_workbook(filename)

    # Get the first worksheet
    ws = wb.worksheets[0]

    # Get the number of columns in the worksheet
    num_cols = ws.max_column

    # Iterate over each column in the worksheet
    for col_num in range(1, num_cols + 1):
        
        if col_num in excludeMerge:
            continue
        
        lastCell = ""
        startIdx = 1
        endIdx = 1
        
        values = [ws.cell(row=row_num, column=col_num).value for row_num in range(1, ws.max_row + 1)]
        
        for i, value in enumerate(values):
            
            if value == lastCell :
                endIdx = i+1
                
            else:
                ws.merge_cells(start_row=startIdx, start_column=col_num, end_row=endIdx, end_column=col_num)
                
                lastCell = value
                startIdx = i+1
                endIdx = i+1
                
        ws.merge_cells(start_row=startIdx, start_column=col_num, end_row=endIdx, end_column=col_num)
        
    wb.save(filename)

def mergeCellsInExcellV2(ws, merge_col, start_row, end_row):
    
    num_cols = ws.max_column
    
    lastCell = ws.cell(row=start_row, column=merge_col).value
    startIdx = start_row
    endIdx = start_row
    
    if merge_col <= num_cols and start_row != end_row:
        for i in range(start_row, end_row+1):
            
            cellValue = ws.cell(row=i, column=merge_col).value
            
            if lastCell == cellValue :
                endIdx = i
            
            else:
                ws.merge_cells(start_row=startIdx, start_column=merge_col, end_row=endIdx, end_column=merge_col)
                mergeCellsInExcellV2(ws=ws, merge_col=merge_col+1, start_row=startIdx, end_row=endIdx)
                
                lastCell = cellValue
                startIdx = i
                endIdx = i
            
        ws.merge_cells(start_row=startIdx, start_column=merge_col, end_row=endIdx, end_column=merge_col)
        mergeCellsInExcellV2(ws=ws, merge_col=merge_col+1, start_row=startIdx, end_row=endIdx)
    
    else:
        pass
    
def SaveDataframeToReport(dataFrame, fileName, fileType="csv"):
    
    res = dataFrame

    if fileType == "json":
        res.to_json(f"{os.getcwd()}/reports/{fileName}.json", orient="records")

    elif fileType == "csv":
        res.to_csv(f"{os.getcwd()}/reports/{fileName}.csv", index=False)

    elif fileType == "excel":
        res.to_excel(f"{os.getcwd()}/reports/{fileName}.xlsx", index=False)
        
        mergeExcell = str(input("\nDo you want to merge the excell sheet (y/n)?"))
        
        if mergeExcell == "Y" or mergeExcell == "y":
            
            wb = openpyxl.load_workbook(f"{os.getcwd()}/reports/{fileName}.xlsx")
            ws = wb.worksheets[0]
            num_rows = ws.max_row
            
            mergeCellsInExcellV2(ws=ws, merge_col=1, start_row=1, end_row=num_rows)
            
            wb.save(f"{os.getcwd()}/reports/{fileName}.xlsx")
        
    elif fileType == "html":
        with open(f"{os.getcwd()}/reports/{fileName}.html", "w", encoding="utf-8") as f:
            f.write(buildHtmlReport(res, title=fileName))

    else:
        print("Error : Invalid File type")

def removeDuplicateExcellCells(dataframe):

    # Load the Excel file into a pandas DataFrame
    df = dataframe

    merged_rows = []
    
    for col in df.columns:
        
        values = df[col].values
        
        lastCell = ""
        
        for i, value in enumerate(values):
            
            if value == lastCell :
                df.iloc[i, df.columns.get_loc(col)] = ""
            else:
                lastCell = value
                
    return df

def split_array(list_a, chunk_size):

  list_chunked = [list_a[i:i + chunk_size] for i in range(0, len(list_a), chunk_size)]

  return list_chunked