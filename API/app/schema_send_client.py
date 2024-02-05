#!/usr/bin/env python3
import sys

import openai
from .security import enviroment
from .google_sheet_imp import Document_CRUD
from typing import List
from pydantic import BaseModel, create_model, Field
from typing import Any, Dict, List
import json, os
import numpy as np

"""
 This is an auto schema definition. When the user defines their column names, the AI determine if that field is String, Boolean or Integer from the names 
 and define schema


"""

SheetReader = Document_CRUD("1kpj7e08JrhsH4WKJhQeIYXWUh4k4Nc4vKSd-DuZqpVw")

API_KEY = enviroment.env_variable["OpenAI_Apikey"]
openai.api_key = API_KEY

def predict_column_data_types(columns: List[str]):
    predictions = {}

    for name in columns:
        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",  # In this case, we use gpt-3.5-turbo-instruct model
                prompt=f"What is the most likely data type for a database column named '{name}'? Choose from: string, integer, boolean.",
                max_tokens=10
            )
            predicted_type = response.choices[0].text.strip().lower()

            # Extract "string", "integer", or "boolean" from the response
            if "integer" in predicted_type:
                predictions[name] = "integer"
            elif "boolean" in predicted_type:
                predictions[name] = "boolean"
            else:
                predictions[name] = "string"
        except Exception as e:
            print(f"Error while processing column '{name}': {e}")
            predictions[name] = "unknown"

    return predictions


def schema_definition(columns: List[str]):
    data_types = predict_column_data_types(columns)

    # Here we set how we convert those "default" values as we want
    result_def = []
    for col_name, value in data_types.items():
        if value == 'string': result_def.append({f"{col_name}":'string'})
        elif value == 'boolean': result_def.append({f"{col_name}":False})
        elif value == 'integer': result_def.append({f"{col_name}":0})
        elif value == 'unknown': result_def.append({f"{col_name}": None})

    return dict({'clientes': result_def})


def client_schema_definition():
    # Get Column Names
    column_names_status = SheetReader.get_all_columns_name_and_status()

    # Get only the names, set lower and replace spaces to "_"
    column_names = np.array([str(name.get('value', None)).lower().replace(" ", "_") for name in column_names_status])

    # Drop None values (if there are)
    mask = column_names != None
    column_names = column_names[mask]

    # Define the schema and column dtype
    schema_client_definition = schema_definition(column_names)
    colum_dtype = np.array([list(dtype.values())[0] for dtype in schema_client_definition.get('clientes', None)])
    
    # Get column unique or not
    colum_unique_or_no = np.array([bool(name.get('is_italic', None)) for name in column_names_status])

    # Get final result in 2D array
    final_result = np.vstack((column_names, colum_dtype, colum_unique_or_no))

    final_schema = []
    # Drop nan values and convert into a json
    for i in range(len(column_names)):
        if final_result[:, i][0] == 'none':
            continue
        else:
            final_schema.append({
                'column_name': final_result[:, i][0],
                'dtype': final_result[:, i][1],
                'is_unique': final_result[:, i][2]
            })

    # Save the json result
    with open(os.path.join('app','config','schema_client.json'),'w') as f:
        f.write(json.dumps(final_schema))
    
    return final_schema

def get_schema_columns():
    with open(os.path.join('app','config','schema_client.json'), 'r') as f:
        column_data = json.load(f)

    return [col_name.get('column_name', None) for col_name in column_data]

############## DEFINE THE CLIENT SCHEMA IN PYDANTIC ##########################

def map_dtype_python_type(dtype: str):
    if dtype == 'string':
        return (str, ...)
    elif dtype == 'integer':
        return (int, ...)
    elif dtype == 'boolean':
        return (bool, ...)
    else:
        return (str, ...)  # Default to string if the dtype is not recognized

def create_client_model():
    with open(os.path.join('app', 'config', 'schema_client.json'), 'r') as f:
        column_data = json.load(f)

    fields = {}
    for col in column_data:
        python_type, default = map_dtype_python_type(col["dtype"])
        is_unique = col["is_unique"] == "True"
        fields[col["column_name"]] = (python_type, Field(default, unique=is_unique))

    dynamic_client_model = create_model('single_client', **fields)
    return dynamic_client_model

def create_dynamic_model():
    single_client_schema = create_client_model()
    class CreateClientsSchema(BaseModel):
        clientes: list[single_client_schema]

    return CreateClientsSchema

ClientSchema = create_dynamic_model()


if __name__ == "__main__":
    print(ClientSchema.schema_json(indent=2))