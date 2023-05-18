import datetime

from io import BytesIO, BufferedWriter

import requests

from time import perf_counter, sleep

from pycortexintelligence.core.messages import *

def _make_url_auth(plataform_url):
    return "https://{}/service/integration-authorization-service.login".format(plataform_url)


def _make_download_url(plataform_url):
    return 'https://{}/service/integration-cube-service.download?'.format(plataform_url)

class LoadExecution:
    def __init__(self, loadmanager_url, auth_headers, execution_id, timeout):
        self.loadmanager = loadmanager_url
        self.headers = auth_headers
        self.id = execution_id
        self.timeout = timeout
    
    def start_process(self):
        endpoint = self.loadmanager + "/execution/" + self.id + "/start"
        response = requests.put(endpoint, headers=self.headers)
        response.raise_for_status()

    def execution_history(self):
        endpoint = self.loadmanager + "/execution/" + self.id
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def check_finished(self):
        history = self.execution_history()
        complete = history['completed']
        if complete == False:
            return False
        
        if 'success' not in history or history['success'] == False:
            msg = "Error on Load execution id: {}".format(history['executionId'])
            errors = history['errors']
            for error in errors:
                msg += "\nError on file id: {}, code: {}, value: {}".format(error['fileId'], error['description'], error['value'])
            raise Exception(msg)
        
        return True
    
    def wait_until_finished(self):
        start_time = perf_counter()
        complete = self.check_finished()
        while complete == False:
            sleep(5)
            current_time = perf_counter()
            if((current_time - start_time) > self.timeout):
                break
            complete = self.check_finished()
    
    def send_file(self, file_like_object, data_format):
        endpoint = self.loadmanager + "/execution/" + self.id + "/file"
        response = requests.post(
            endpoint,
            headers=self.headers,
            data=data_format,
            files={"file": file_like_object},
        )
        response.raise_for_status()

class LoadManager:
    def __init__(self, plataform_url, username, password, useSsl = True):
        self.protocol = "https" if useSsl else "http"
        self.plataform_url = plataform_url
        self.username = username
        self.password = password
        self.loadmanager = self.get_url()
        self.credentials = self.get_platform_token()
    
    def get_platform_token(self):
        url = "{}://{}/service/integration-authorization-service.login".format(self.protocol, self.plataform_url)
        credentials = {"login": str(self.username), "password": str(self.password)}
        response = requests.post(url, json=credentials)
        response.raise_for_status()
        response_json = response.json()
        return {"Authorization": "Bearer " + response_json["key"]}
    
    def get_url(self):
        url =  "{}://{}/service/platform-collector-information/".format(self.protocol, self.plataform_url)
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
        if "loadManager.url" in response_json:
            return response_json["loadManager.url"]
        raise Exception("LoadManager not supported!")
    
    def create_load_execution(self, destination_id, file_processing_timeout, ignore_validation_errors, execution_parameters):
        endpoint = "{}/execution".format(self.loadmanager)
        content = {
            "destinationId": destination_id,
            "fileProcessingTimeout": file_processing_timeout,
            "ignoreValidationErrors": ignore_validation_errors
            , **execution_parameters
        }
        response = requests.post(endpoint, headers=self.credentials, json=content)
        response.raise_for_status()
        execution_id = response.json()["executionId"]
        return LoadExecution(self.loadmanager, self.credentials, execution_id, file_processing_timeout)


def upload_file_to_cube(cubo_id,
                        file_like_object,
                        plataform_url,
                        username,
                        password,
                        data_format,
                        file_processing_timeout,
                        execution_parameters={
                            'name': 'LoadManager PyCortex',
                        },
                        ignore_validation_errors=False
                        ):
    """
    :param timeout:
    :param cubo_id:
    :param file_like_object:
    :param auth_endpoint:
    :param credentials:
    :param loadmanager:
    :param data_format:
    :return:
    """

    # =============== New LoadManager instance =================
    load_manager = LoadManager(plataform_url, username, password, False)

    # ================ Get New Execution =======================
    load_execution = load_manager.create_load_execution(cubo_id, file_processing_timeout, ignore_validation_errors, execution_parameters)

    # ================ Send files =============================
    load_execution.send_file(file_like_object, data_format)

    # ================ Start Data Input Process ===========================
    load_execution.start_process()

    return load_execution


def upload_to_cortex(**kwargs):
    """
    :param cubo_id:
    :param file_like_object:
    :param plataform_url:
    :param username:
    :param password:
    :param data_format: data_format={
                            "charset": "UTF-8",
                            "quote": "\"",
                            "escape": "\\",
                            "delimiter": ",",
                            "fileType": "CSV",
                            "compressed": "NONE"
                        }
    :param timeout: {
        'file': 300
    }
    :return:
    """
    # Read Kwargs
    cubo_id = kwargs.get('cubo_id')
    file_path = kwargs.get('file_path')
    plataform_url = kwargs.get('plataform_url')
    username = kwargs.get('username')
    password = kwargs.get('password')
    file_like_object = kwargs.get('file_like_object')

    if not file_path and not file_like_object:
        raise ValueError(INVALID_FILES_ERROR, f'FORAM PASSADOS: {file_path}, {file_like_object}')
    if not file_like_object:
        file_like_object = open(file_path, "rb")

    data_format = kwargs.get('data_format', {
        "charset": "UTF-8",
        "quote": "\"",
        "escape": "\\",
        "delimiter": ",",
        "fileType": "CSV",
        "compressed": "NONE"
    })
    timeout = kwargs.get('timeout', {
        'file': 300
    })
    execution_parameters = kwargs.get('execution_parameters', {
        'name': 'LoadManager PyCortex',
    })
    datainput_parameters = kwargs.get('datainput_parameters', {
        'ignoreValidationErrors': False
    })

    if 'file' not in timeout.keys() and 'execution' not in timeout.keys():
        raise ValueError(FORMAT_TIMEOUT)

    # Verify Kwargs
    if cubo_id and file_like_object and plataform_url and username and password:
        load_execution = upload_file_to_cube(
            cubo_id=cubo_id,
            file_like_object=file_like_object,
            plataform_url=plataform_url,
            username=username,
            password= password,
            data_format=data_format,
            file_processing_timeout=int(timeout['file']),
            execution_parameters=execution_parameters,
            ignore_validation_errors=datainput_parameters['ignoreValidationErrors'],
        )
        
        load_execution.check_finished()

    else:
        raise ValueError(ERROR_ARGUMENTS_VALIDATION)


def download_from_cortex(**kwargs):
    """
    :param cubo_id:
    :param cubo_name:
    :param plataform_url:
    :param username:
    :param password:
    :param columns:
    :param file_path:
    :param data_format:
    :param filters:
    :return:
    """
    cubo_id = kwargs.get('cubo_id')
    cubo_name = kwargs.get('cubo_name')
    plataform_url = kwargs.get('plataform_url')
    username = kwargs.get('username')
    password = kwargs.get('password')
    columns = kwargs.get('columns')
    file_path = kwargs.get('file_path')
    file_like_object = kwargs.get('file_like_object')
    data_format = kwargs.get('data_format', {
        "charset": "UTF-8",
        "quote": "\"",
        "escape": "\\",
        "delimiter": ",",
    })
    filters = kwargs.get('filters', None)

    if not file_like_object:
        if isinstance(file_path, BytesIO):
            file_like_object = BytesIO()
        else:
            file_like_object = open(file_path, 'wb')
    if cubo_id and cubo_name:
        raise ValueError(DOWNLOAD_ERROR_JUST_ID_OR_NAME)
    if (cubo_id or cubo_name) and plataform_url and username and password and columns and (file_path or file_like_object):
        # Verify is a ID or Name
        if cubo_id:
            cube = '{"id":"' + cubo_id + '"}'
        else:
            cube = '{"name":"' + cubo_name + '"}'

        # Columns to Download
        columns_download = []
        for column in columns:
            columns_download.append({
                "name": column,
            })
        columns_download = str(columns_download).replace("'", '"')

        # Need to Apply Filters
        if filters:
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
                        value = value.split('-')
                        date_start = datetime.datetime.strptime(value[0], "%d/%m/%Y")
                        date_end = datetime.datetime.strptime(value[1], "%d/%m/%Y")
                        element["type"] = "DATE"
                        element["rangeStart"] = date_start.strftime("%Y%m%d")
                        element["rangeEnd"] = date_end.strftime("%Y%m%d")
                    except ValueError:
                        value = value_temp.split('|')
                        element["value"] = value
                filters_download.append(element)
            filters_download = str(filters_download).replace("'", '"')

        auth_endpoint = _make_url_auth(plataform_url)
        credentials = {"login": str(username), "password": str(password)}
        auth_post = requests.post(auth_endpoint, json=credentials)
        headers = {
            'x-authorization-user-id': auth_post.json()['userId'],
            'x-authorization-token': auth_post.json()['key']
        }
        download_endpoint = _make_download_url(plataform_url)
        payload = {
            'cube': cube,
            'charset': data_format['charset'],
            'delimiter': data_format['delimiter'],
            'quote': data_format['quote'],
            'escape': data_format['escape'],
        }
        if filters:
            payload['filters'] = filters_download
        if columns_download:
            payload['headers'] = columns_download

        with requests.get(download_endpoint, stream=True, headers=headers, params=payload) as r:
            content_rows = r.headers["Content-Rows"]
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                file_like_object.write(chunk)
            file_like_object.flush()
        
        if isinstance(file_like_object, BufferedWriter):
            return content_rows

        if isinstance(file_like_object, BytesIO):
            return file_like_object, content_rows
    else:
        raise ValueError(ERROR_ARGUMENTS_VALIDATION)

