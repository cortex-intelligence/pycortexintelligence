import datetime
import json
import logging
from http import HTTPStatus
from io import BufferedWriter, BytesIO
from typing import Any, BinaryIO, Dict, List, Optional, Union

import requests

from pycortexintelligence.core.messages import (
    DOWNLOAD_ERROR_JUST_ID_OR_NAME,
    ERROR_ARGUMENTS_VALIDATION,
)


class ApplicationTenantFilter(logging.Filter):
    def __init__(self, application_name, tenant):
        self.application_name = application_name
        self.tenant = tenant

    def filter(self, record):
        record.Application = self.application_name
        record.tenant = self.tenant
        return True


class LoadExecution:
    loadmanager_url = "https://api.cortex-intelligence.com"

    def __init__(
        self,
        cube_id,
        header,
        file_processing_timeout,
        ignore_validation_errors,
        executor_name,
        file_like_object,
        data_format,
    ):
        self.cube_id = cube_id
        self.header = header
        self.file_processing_timeout = file_processing_timeout
        self.ignore_validation_errors = ignore_validation_errors
        self.executor_name = executor_name
        self.file_like_object = file_like_object
        self.data_format = data_format

    def start_process(self):
        endpoint = self.loadmanager_url + "/execution/" + self.execution_id + "/start"
        response = requests.put(endpoint, headers=self.header)
        response.raise_for_status()

    @classmethod
    def execution_history(cls, headers, execution_id):
        endpoint = cls.loadmanager_url + "/execution/" + execution_id
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()

    @classmethod
    def check_finished(cls, headers, execution_id) -> bool:
        history = cls.execution_history(headers, execution_id)
        complete = history["completed"]
        if not complete:
            return False

        if "success" not in history or history["success"] is False:
            msg = "Error on Load execution id: {}".format(history["executionId"])
            errors = history["errors"]
            for error in errors:
                msg += "\nError on file id: {}, code: {}, value: {}".format(
                    error["fileId"], error["description"], error["value"]
                )
            raise Exception(msg)

        return True

    def send_file(self):
        endpoint = self.loadmanager_url + "/execution/" + self.execution_id + "/file"
        response = requests.post(
            endpoint,
            headers=self.header,
            data=self.data_format,
            files={"file": self.file_like_object},
        )
        response.raise_for_status()

    def create_load_execution(self) -> str:
        endpoint = f"{self.loadmanager_url}/execution"
        content = {
            "destinationId": self.cube_id,
            "fileProcessingTimeout": self.file_processing_timeout,
            "ignoreValidationErrors": self.ignore_validation_errors,
            "name": self.executor_name,
        }
        response = requests.post(endpoint, headers=self.header, json=content)
        response.raise_for_status()
        self.execution_id = response.json()["executionId"]
        return self.execution_id


class PyCortex:
    data_format = {
        "charset": "UTF-8",
        "quote": '"',
        "escape": "\\",
        "delimiter": ",",
        "fileType": "CSV",
        "compressed": "NONE",
    }
    executor_name = "LoadManager PyCortex"
    file_processing_timeout = 300
    ignore_validation_errors = False

    @classmethod
    def upload_to_cortex(
        cls,
        cube_id: str,
        platform_url: str,
        username: str,
        password: str,
        file_object: Union[str, BinaryIO],
        is_file=True,
        **kwargs,
    ) -> Dict:
        if is_file and isinstance(file_object, str):
            file_object = open(file_object, "rb")

        elif not is_file and isinstance(file_object, BytesIO):
            file_object.seek(0)

        else:
            raise ValueError(
                f"A combinação is_file={is_file} com o tipo {type(file_object)} do file_object não é permitida."
            )

        file_processing_timeout = int(kwargs.get("timeout", cls.file_processing_timeout))
        ignore_validation_errors = kwargs.get("ignore_errors", cls.ignore_validation_errors)
        executor_name = kwargs.get("executor_name", cls.executor_name)

        header = cls.platform_auth(platform_url, username, password)

        load_execution = LoadExecution(
            cube_id=cube_id,
            header=header,
            file_processing_timeout=file_processing_timeout,
            ignore_validation_errors=ignore_validation_errors,
            executor_name=executor_name,
            file_like_object=file_object,
            data_format=cls.data_format,
        )
        execution_id = load_execution.create_load_execution()
        load_execution.send_file()
        load_execution.start_process()
        return LoadExecution.execution_history(headers=header, execution_id=execution_id)

    @staticmethod
    def make_filter(filters: List):
        filters_download = []
        for filter in filters:
            column_name = filter[0]
            value = filter[1]
            element = {
                "name": column_name,
                "type": "SIMPLE",
            }
            try:
                value = datetime.datetime.strptime(value, "%d/%m/%Y")
                element["type"] = "DATE"
                element["rangeStart"] = value.strftime("%Y%m%d")
                element["rangeEnd"] = value.strftime("%Y%m%d")
            except ValueError:
                value_temp = value
                try:
                    value = value.split("-")  # type: ignore
                    date_start = datetime.datetime.strptime(value[0], "%d/%m/%Y")
                    date_end = datetime.datetime.strptime(value[1], "%d/%m/%Y")
                    element["type"] = "DATE"
                    element["rangeStart"] = date_start.strftime("%Y%m%d")
                    element["rangeEnd"] = date_end.strftime("%Y%m%d")
                except ValueError:
                    value = value_temp.split("|")  # type: ignore
                    element["value"] = value
            filters_download.append(element)
        return json.dumps(filters_download, ensure_ascii=False)

    @staticmethod
    def platform_auth(platform_url: str, username: str, password: str, return_user_id=False):
        if not (username and password and platform_url):
            raise ValueError(ERROR_ARGUMENTS_VALIDATION)

        credentials = {"login": username, "password": password}

        auth_endpoint = f"https://{platform_url}/service/integration-authorization-service.login"
        auth_post = requests.post(auth_endpoint, json=credentials).json()
        if return_user_id:
            return {
                "x-authorization-user-id": auth_post["userId"],
                "x-authorization-token": auth_post["key"],
            }
        else:
            return {"Authorization": f"Bearer {auth_post['key']}"}

    @staticmethod
    def _make_cube_provider_url(platform_url: str):
        return f"https://{platform_url}/service/rpc/cube-provider-service.load"

    @classmethod
    def return_field_metadata(cls, field, platform_url, cube_id, header) -> dict:
        provider_url = cls._make_cube_provider_url(platform_url)
        resp = requests.post(provider_url, headers=header, json={"id": cube_id})
        resp.raise_for_status()
        for dim in resp.json()["dimensions"]:
            if dim["name"] == field:
                dimension = dim
                break
        try:
            return dimension
        except UnboundLocalError:
            raise Exception("A dimensão não existe nesta tabela.")

    @classmethod
    def download_from_cortex_via_diego(
        cls,
        cube_id: str,
        platform_url: str,
        username: str,
        password: str,
        filters: dict,
        exact_match: str = "true",
    ):
        field = list(filters.keys())[0]
        header = cls.platform_auth(platform_url, username, password, return_user_id=True)
        dim = cls.return_field_metadata(field, platform_url, cube_id, header)
        body = {
            "filterList": [
                {
                    "id": dim["id"],
                    "name": dim["name"],
                    "type": dim["type"],
                    "exactMatch": exact_match,
                    "value": list(filters.values())[0],
                }
            ]
        }
        response = requests.post(
            f"https://{platform_url}/controller/cube/{cube_id}/dump",
            headers=header,
            json=body,
        )
        properties = response.json()["properties"]
        data_format = {
            "encoding": properties["charset"],
            "quotechar": properties["quote"],
            "escapechar": properties["escape"],
            "sep": properties["delimiter"],
            "fileType": properties["fileType"],
            "compressed": properties["compression"],
        }
        path = response.json()["path"].replace("s3://", "").split("/", 1)
        return path[0], path[1], data_format

    @staticmethod
    def make_df_from_bi(bi_bucket, bi_s3key, properties):
        import boto3
        import pandas as pd

        s3 = boto3.resource("s3")
        my_bucket = s3.Bucket(bi_bucket)

        dataframe = pd.DataFrame()

        for objects in my_bucket.objects.filter(Prefix=bi_s3key):
            print(objects.key)
            s3_object = s3.Object(bucket_name=bi_bucket, key=objects.key)
            s3_response = s3_object.get()
            s3_object_body = s3_response.get("Body")
            content = s3_object_body.read()

            temp_df = pd.read_csv(
                BytesIO(content),
                sep=properties["sep"],
                quotechar=properties["quotechar"],
                escapechar=properties["escapechar"].replace("\\\\", "\\"),
                encoding=properties["encoding"],
                compression=properties["compressed"].lower(),
            )
            dataframe = pd.concat([dataframe, temp_df], axis=0).reset_index(drop=True)
        return dataframe

    @classmethod
    def download_from_cortex(
        cls,
        platform_url: str,
        username: str,
        password: str,
        file_object: BytesIO or str,
        cube_id: Optional[str] = None,
        cube_name: Optional[str] = None,
        filters: Optional[List] = None,
        columns: Union[List, str] = "*",
    ) -> Any:
        if not isinstance(file_object, BytesIO):
            file_object = open(file_object, "wb")  # type: ignore

        if cube_id and cube_name:
            raise ValueError(DOWNLOAD_ERROR_JUST_ID_OR_NAME)

        if (cube_id or cube_name) and file_object and columns:
            if cube_id:
                cube = f'{{"id":"{cube_id}"}}'
            else:
                cube = f'{{"name":"{cube_name}"}}'

            payload = {
                "cube": cube,
                "charset": cls.data_format["charset"],
                "delimiter": cls.data_format["delimiter"],
                "quote": cls.data_format["quote"],
                "escape": cls.data_format["escape"],
            }

            if isinstance(columns, List):
                columns_download = json.dumps([{"name": column} for column in columns], ensure_ascii=False)
                payload["headers"] = columns_download

            if isinstance(columns, str):
                if columns != "*":
                    payload["headers"] = json.dumps({"name": columns}, ensure_ascii=False)

            filters_download = list()
            if filters:
                filters_download = cls.make_filter(filters)
                payload["filters"] = filters_download

            headers = cls.platform_auth(platform_url, username, password, return_user_id=True)
            download_endpoint = cls._make_download_url(platform_url)

            with requests.get(url=download_endpoint, stream=True, headers=headers, params=payload) as r:
                r.raise_for_status()
                try:
                    content_rows = r.headers["Content-Rows"]
                except KeyError:
                    raise Exception(
                        f"Não foi possível realizar o download.\nStatus Code:{r.status_code}\nResponse:{r.content}"
                    )
                chunks_len = list()
                for chunk in r.iter_content(chunk_size=8192):
                    chunks_len.append(chunk)
                    file_object.write(chunk)

                file_object.flush()

            if isinstance(file_object, BufferedWriter):
                return content_rows

            if isinstance(file_object, BytesIO):
                return file_object, content_rows
        else:
            raise ValueError(ERROR_ARGUMENTS_VALIDATION)

    @classmethod
    def get_exported_file_info(cls, platform_url: str, username: str, password: str, filters: Dict):
        url = f"https://{platform_url}/controller/data-credit-control/data-credit-operation/query-exported"
        auth_header = cls.platform_auth(platform_url, username, password, return_user_id=True)
        response = requests.post(url, json=filters, headers=auth_header)
        response.raise_for_status()
        return response.json()

    @classmethod
    def download_exported_file(cls, platform_url: str, username: str, password: str, operation_id: str):
        url = f"https://{platform_url}/controller/data-credit-control/data-credit-operation/{operation_id}/download"
        auth_header = cls.platform_auth(platform_url, username, password, return_user_id=True)
        return requests.get(url, headers=auth_header)

    @classmethod
    def delete_from_cortex(
        cls,
        cube_id: str,
        platform_url: str,
        username: str,
        password: str,
        filters: Optional[List] = None,
    ):
        auth_header = cls.platform_auth(platform_url, username, password, return_user_id=True)
        payload = {"cube": f'{{"id": "{cube_id}"}}', "filters": list()}

        if filters is None:
            payload["filters"] = [{"name": "# Records", "type": "SIMPLE", "value": 1}]

        if filters is not None:
            payload["filters"] = cls.make_filter(filters)

        delete_url = f"https://{platform_url}/service/integration-cube-service.delete"

        response = requests.get(delete_url, params=payload, headers=auth_header)

        if response.status_code == HTTPStatus.OK:
            return response.status_code

        if response.status_code != HTTPStatus.OK:
            raise ValueError(f"O status code recebido, foi: {response.status_code}\n {response.content}")

    @staticmethod
    def _make_download_url(platform_url: str):
        return f"https://{platform_url}/service/integration-cube-service.download?"


def download_from_cortex(**kwargs) -> Any:
    import warnings

    warnings.warn(
        "\n\nThis module will be deprecated in the next release. Please use `PyCortex.download_from_cortex`.\n\n",
        DeprecationWarning,
        stacklevel=2,
    )
    if "file_like_object" in kwargs:
        file_object = kwargs.get("file_like_object")
    elif "file_path" in kwargs:
        file_object = kwargs.get("file_path")

    return PyCortex.download_from_cortex(
        cube_id=kwargs.get("cubo_id"),  # type: ignore
        platform_url=kwargs.get("plataform_url"),  # type: ignore
        username=kwargs.get("username"),  # type: ignore
        password=kwargs.get("password"),  # type: ignore
        columns=kwargs.get("columns"),  # type: ignore
        filters=kwargs.get("filters"),  # type: ignore
        file_object=file_object,  # type: ignore
    )


def upload_to_cortex(**kwargs):
    import warnings

    warnings.warn(
        "This module is deprecated. Please use `PyCortex.upload_to_cortex`.",
        DeprecationWarning,
        stacklevel=2,
    )

    return PyCortex.upload_to_cortex(
        cube_id=kwargs["cubo_id"],
        platform_url=kwargs["plataform_url"],
        username=kwargs["username"],
        password=kwargs["password"],
        file_object=kwargs["file_path"],
    )
