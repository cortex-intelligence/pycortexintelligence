import os
from http import HTTPStatus
from io import BytesIO

import pkg_resources
from conftest import make_file_or_bytesio
from dotenv import load_dotenv
from pytest import mark, raises

from pycortexintelligence.functions import PyCortex, download_from_cortex

load_dotenv()

default_data_format = {
    "charset": "UTF-8",
    "quote": '"',
    "escape": "\\/\\/",
    "delimiter": ",",
}
skip_version_100 = {
    "condition": pkg_resources.get_distribution("pycortexintelligence").version >= "1.0.0",
    "reason": "Método de chamada utilizado na nova versão.",
}

skip_version_022 = {
    "condition": pkg_resources.get_distribution("pycortexintelligence").version < "1.0.0",
    "reason": "Método de chamada utilizado na nova versão.",
}


def read_csv_from_bytesio(files):
    col_1 = list()
    for data in files.readlines():
        col_1.append(data.decode().strip().split(",")[0])
    return len(col_1) - 1


def read_csv_from_file(path):
    col_1 = list()
    col_2 = list()
    with open(path) as _csv:
        for data in _csv.readlines():
            col_1.append(data.strip().split(",")[0])
            col_2.append(data.strip().split(",")[1])

    return len(col_1) - 1


def test_download_from_cortex_assert_quant_linhas_baixadas():
    path = "teste_download.csv"
    content_rows = download_from_cortex(
        cubo_id=os.getenv("cube_id"),
        plataform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_path=path,
        data_format=default_data_format,
        columns=[
            "ID Cortex",
            "Data de publicação",
        ],
        filters=[
            ["Data", "20/05/2023-21/05/2023"],
        ],
    )
    length = read_csv_from_file(path)
    assert int(content_rows) == length
    os.remove(path)


def test_download_from_cortex_assert_quant_linhas_baixadas_via_bytesio():
    files, content_rows = download_from_cortex(
        cubo_id=os.getenv("cube_id"),
        plataform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_path=BytesIO(),
        data_format=default_data_format,
        columns=[
            "ID Cortex",
            "Data de publicação",
        ],
        filters=[
            ["Data", "20/05/2023-21/05/2023"],
        ],
    )
    files.seek(0)
    length = read_csv_from_bytesio(files)
    assert int(content_rows) == length


def test_download_from_cortex_assert_file_exists():
    path = "download_teste.csv"
    download_from_cortex(
        cubo_id=os.getenv("cube_id"),
        plataform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_path=path,
        data_format=default_data_format,
        columns=[
            "ID Cortex",
            "Data de publicação",
        ],
        filters=[
            ["Data", "20/05/2023-21/05/2023"],
        ],
    )
    assert os.path.exists(path)
    os.remove(path)


@mark.skipif(**skip_version_022)
def test_download_from_cortex_assert_quant_linhas_chamada_nova():
    files, content_rows = PyCortex.download_from_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=BytesIO(),
        columns=[
            "ID Cortex",
            "Data de publicação",
        ],
        filters=[
            ["Data", "20/05/2023-21/05/2023"],
        ],
    )
    files.seek(0)
    length = read_csv_from_bytesio(files)
    assert int(content_rows) == length


@mark.skipif(**skip_version_022)
@mark.download_test
def test_download_from_cortex_passando_cube_id():
    files, content_rows = PyCortex.download_from_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=BytesIO(),
        columns=[
            "ID Cortex",
            "Data de publicação",
        ],
        filters=[
            ["Data", "20/05/2023-21/05/2023"],
        ],
    )
    files.seek(0)
    length = read_csv_from_bytesio(files)
    assert int(content_rows) == length


@mark.skipif(**skip_version_022)
@mark.download_test
def test_download_from_cortex_passando_cube_name():
    files, content_rows = PyCortex.download_from_cortex(
        cube_name=os.getenv("cube_name"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=BytesIO(),
        columns=[
            "ID Cortex",
            "Data de publicação",
        ],
        filters=[
            ["Data", "20/05/2023-21/05/2023"],
        ],
    )
    files.seek(0)
    length = read_csv_from_bytesio(files)
    assert int(content_rows) == length


@mark.skipif(**skip_version_022)
@mark.download_test
@mark.xfail
def test_download_from_cortex_passando_cube_name_cube_id():
    with raises(ValueError):
        files, content_rows = PyCortex.download_from_cortex(
            cube_name=os.getenv("cube_name"),
            cube_id=os.getenv("cube_id"),
            platform_url=os.getenv("platform_url"),
            username=os.getenv("username"),
            password=os.getenv("password"),
            file_object=BytesIO(),
            columns=[
                "ID Cortex",
                "Data de publicação",
            ],
            filters=[
                ["Data", "20/05/2023-21/05/2023"],
            ],
        )
        files.seek(0)
        length = read_csv_from_bytesio(files)
        assert int(content_rows) == length


@mark.skipif(**skip_version_022)
@mark.download_test
@mark.xfail
def test_download_from_cortex_nao_passando_cube_name_cube_id():
    with raises(ValueError):
        files, content_rows = PyCortex.download_from_cortex(
            platform_url=os.getenv("platform_url"),
            username=os.getenv("username"),
            password=os.getenv("password"),
            file_object=BytesIO(),
            columns=[
                "ID Cortex",
                "Data de publicação",
            ],
            filters=[
                ["Data", "20/05/2023-21/05/2023"],
            ],
        )
        files.seek(0)
        length = read_csv_from_bytesio(files)
        assert int(content_rows) == length


@mark.skipif(**skip_version_022)
def test_download_from_cortex_passando_cube_passando_parametros():
    files, content_rows = PyCortex.download_from_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=BytesIO(),
        columns=[
            "ID Cortex",
            "Data de publicação",
        ],
        filters=[
            ["Data", "20/05/2023-21/05/2023"],
        ],
        delimiter=";",
        quote="'",
    )
    files.seek(0)
    length = read_csv_from_bytesio(files)
    assert int(content_rows) == length


@mark.skipif(**skip_version_022)
def test_upload_to_cortex_chamada_nova(save_file_temp_data):
    from time import sleep

    from pycortexintelligence.functions import PyCortex

    response = PyCortex.upload_to_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=save_file_temp_data,
        exec_name="PyCortex under Test",
    )
    sleep(10)
    print(response)
    assert isinstance(response, dict)


@mark.skipif(**skip_version_022)
@mark.parametrize("fileobject,isfile", [(make_file_or_bytesio(False), True), (make_file_or_bytesio(True), False)])
def test_validacao_upload_inputs_file_object_e_is_file_com_exception(fileobject, isfile):
    with raises(ValueError):
        PyCortex.upload_to_cortex(
            cube_id=os.getenv("cube_id"),
            platform_url=os.getenv("platform_url"),
            username=os.getenv("username"),
            password=os.getenv("password"),
            file_object=fileobject,
            is_file=isfile,
            exec_name="PyCortex under Test",
        )


@mark.skipif(**skip_version_022)
@mark.parametrize("fileobject,isfile", [(make_file_or_bytesio(True), True), (make_file_or_bytesio(False), False)])
def test_validacao_dos_inputs_file_object_e_is_file_ok(fileobject, isfile):
    response = PyCortex.upload_to_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=fileobject,
        is_file=isfile,
        exec_name="PyCortex under Test",
    )
    assert isinstance(response, dict)


@mark.skipif(**skip_version_022)
def test_upload_to_cortex_chamada_nova_buffer(save_df_to_var_temp_data):
    response = PyCortex.upload_to_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=save_df_to_var_temp_data,
        is_file=False,
        exec_name="PyCortex under Test",
    )
    print(response)
    assert isinstance(response, dict)


@mark.skipif(**skip_version_022)
def test_upload_to_cortex_chamada_nova_timeout(save_df_to_var_temp_data):
    response = PyCortex.upload_to_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        file_object=save_df_to_var_temp_data,
        timeout="300",
        is_file=False,
        exec_name="PyCortex under Test",
    )
    print(response)


@mark.skipif(**skip_version_022)
def test_delete_from_cortex(upload_data_to_cortex):
    _, data = upload_data_to_cortex
    filter_string = "|".join([line.split(",")[0] for line in data[1:]])

    response = PyCortex.delete_from_cortex(
        cube_id=os.getenv("cube_id"),
        platform_url=os.getenv("platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        filters=[["Medida", filter_string]],
    )

    assert response == HTTPStatus.OK


@mark.skipif(**skip_version_022)
def test_get_exported_file_info_response_is_list():
    response = PyCortex.get_exported_file_info(
        platform_url=os.getenv("exported_platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        filters={
            "filters": [
                {"user.login": {"EQUALS": "qualidade.ds"}},
            ],
            "rangeStart": "2023-12-27",
            "rangeEnd": "2023-12-28",
        },
    )

    assert isinstance(response, list)


@mark.skipif(**skip_version_022)
@mark.parametrize("operation_id", ["b15f6536fa734c7ba2086af08d9b2b8d", "b969bc5a6d434708b6912e85c7654916"])
def test_download_exported_file_from_data_credit(operation_id):
    response = PyCortex.download_exported_file(
        platform_url=os.getenv("exported_platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        operation_id=operation_id,
    )

    assert "url" in response.json().keys()


@mark.skipif(**skip_version_022)
def test_download_exported_file_with_contacts():
    response = PyCortex.download_exported_file(
        platform_url=os.getenv("exported_platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        operation_id="b15f6536fa734c7ba2086af08d9b2b8d",
    )

    assert "ctx-static" in response.json()["url"]


@mark.skipif(**skip_version_022)
def test_download_exported_file_without_contacts():
    response = PyCortex.download_exported_file(
        platform_url=os.getenv("exported_platform_url"),
        username=os.getenv("username"),
        password=os.getenv("password"),
        operation_id="b969bc5a6d434708b6912e85c7654916",
    )

    assert "platform-data-credit-control-shared" in response.json()["url"]
