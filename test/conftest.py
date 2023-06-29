import os
from datetime import datetime
from io import BytesIO

import pandas as pd
from faker import Faker
from pytest import fixture


def make_data_to_upload():
    fake = Faker()
    Faker.seed(0)
    dates_list = [fake.date_between(start_date=datetime(2023, 5, 1), end_date="today") for _ in range(5)]
    dates = [ii.strftime("%Y-%m-%d") for ii in dates_list]
    dim_1 = [fake.job() for _ in range(5)]
    dim_2 = [fake.first_name() for _ in range(5)]
    med = [int(_) for _ in range(20, 25)]
    return med, dim_1, dim_2, dates


def make_file_or_bytesio(is_file: bool):
    med, dim_1, dim_2, dates = make_data_to_upload()
    if is_file:
        filepath = "somepath.csv"
        with open(filepath, "w") as csv:
            csv.write("Medida,Dimensão 1,Dimensão 2,Data\n")
            for data in zip(med, dim_1, dim_2, dates):
                csv.write(f'{data[0]},"{data[1]}","{data[2]}","{data[3]}"\n')
        return filepath
    if not is_file:
        df = pd.DataFrame({"Medida": med, "Dimensão 1": dim_1, "Dimensão 2": dim_2, "Data": dates})
        df_var = BytesIO()
        df.to_csv(df_var, index=False)
        return df_var


@fixture
def fixture_make_data_to_upload():
    return make_data_to_upload()


@fixture
def save_file_temp_data(fixture_make_data_to_upload):
    med, dim_1, dim_2, dates = fixture_make_data_to_upload
    filepath = "somepath.csv"
    with open(filepath, "w") as csv:
        csv.write("Medida,Dimensão 1,Dimensão 2,Data\n")
        for data in zip(med, dim_1, dim_2, dates):
            csv.write(f'{data[0]},"{data[1]}","{data[2]}","{data[3]}"\n')
    yield filepath
    os.remove(filepath)


@fixture
def save_df_to_var_temp_data(fixture_make_data_to_upload):
    med, dim_1, dim_2, dates = fixture_make_data_to_upload

    df = pd.DataFrame({"Medida": med, "Dimensão 1": dim_1, "Dimensão 2": dim_2, "Data": dates})
    df_var = BytesIO()
    df.to_csv(df_var, index=False)
    return df_var


@fixture
def upload_data_to_cortex(save_df_to_var_temp_data):
    from time import sleep

    from dotenv import load_dotenv

    from pycortexintelligence.functions import PyCortex

    load_dotenv()

    response = PyCortex.upload_to_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=save_df_to_var_temp_data,
        is_file=False,
        exec_name="PyCortex under Test",
    )
    sleep(20)
    return response
