import datetime

import requests

from time import perf_counter

from pycortexintelligence.core.messages import *

def check_response(response):
    if response.ok == False:
        raise Exception("Request failed! " + response.reason)

def _make_url_auth(plataform_url):
    return "https://{}/service/integration-authorization-service.login".format(plataform_url)


def _make_download_url(plataform_url):
    return 'https://{}/service/integration-cube-service.download?'.format(plataform_url)

class LoadExecution:
    def __init__(self, loadmanager_url, auth_headers, execution_id, timeout):
        self.loadManager = loadmanager_url
        self.headers = auth_headers
        self.id = execution_id
        self.timeout = timeout
    
    def start_process(self):
        endpoint = self.loadmanager + "/execution/" + self.id + "/start"
        response = requests.put(endpoint, headers=self.headers)
        check_response(response)

    def execution_history(self):
        endpoint = self.loadmanager + "/execution/" + self.id
        response = requests.get(endpoint, headers=self.headers)
        check_response(response)
        return response.json()
    
    def wait_until_finished(self):
        start_time = perf_counter()
        history = self.execution_history()
        complete = history['completed']
        while(complete == False):
            current_time = perf_counter()
            if((current_time - start_time) > self.timeout):
                break
            history = self.execution_history()
            complete = history['completed']

        if(history['success'] == True):
            print("Done!")
        else:
            print("Error on Load execution id: " + history['executionId'])
            errors = history['errors']
            for error in errors:
                print("FileID: " + error['fileId'] + ", error code: " + error['description'] + ", description: " + error['value'])
    
    def send_file(self, file_path, data_format):
        endpoint = self.loadmanager + "/execution/" + self.id + "/file"
        response = requests.post(
            endpoint,
            headers=self.headers,
            data=data_format,
            files={"file": open(file_path, "rb")},
        )
        check_response(response)

class LoadManager:
    def __init__(self, plataform_url, username, password, useSsl = True):
        self.protocol = "https" if useSSl else "http"
        self.plataform_url = plataform_url
        self.username = username
        self.password = password
        self.loadManager = self.get_url()
        self.credentials = self.get_platform_token()
    
    def get_platform_token(self, platform_url, username, password):
        url = "{}://{}/service/integration-authorization-service.login".format(self.protocol, self.plataform_url)
        credentials = {"login": str(self.username), "password": str(self.password)}
        response = request.post(url, credentials)
        check_response(response)
        response_json = response.json()
        return {"Authorization": "Bearer " + response_json["key"]}
    
    def get_url(self, platform_url):
        url =  "{}://{}/service/platform-collector-information/".format(self.protocol, plataform_url)
        response = request.get(url)
        check_response(response)
        response_json = response.json()
        if response_json["loadManager.uri"] is None:
            raise Exception("LoadManager not supported!")
        return response_json["loadManager.uri"]
    
    def create_load_execution(self, destination_id, file_processing_timeout, ignore_validation_errors):
        endpoint = "{}/execution".format(self.loadmanager)
        content = {
            "destinationId": destination_id,
            "fileProcessingTimeout": file_processing_timeout,
            "ignoreValidationErrors": ignore_validation_errors
        }
        response = requests.post(endpoint, headers=self.credentials, json=content)
        check_response(response)
        execution_id = response.json()["executionId"]
        return LoadExecution(self.loadManager, self.credentials, execution_id, file_processing_timeout)


def upload_local_2_cube(destination_id,
                        file_path,
                        plataform_url,
                        username,
                        password,
                        data_format,
                        file_processing_timeout,
                        execution_parameters={
                            'name': 'LoadManager PyCortex',
                        },
                        ignore_validation_errors
                        ):
    """
    :param timeout:
    :param destination_id:
    :param file_path:
    :param auth_endpoint:
    :param credentials:
    :param loadmanager:
    :param data_format:
    :return:
    """

    # =============== New LoadManager instance =================
    load_manager = LoadManager(plataform_url, username, password)

    # ================ Get New Execution =======================
    load_execution = load_manager.create_load_execution(destination_id, file_processing_timeout, ignore_validation_errors)

    # ================ Send files =============================
    load_execution.send_file(file_path, data_format)

    # ================ Start Data Input Process ===========================
    load_execution.start_process()

    return load_execution


def upload_to_cortex(**kwargs):
    """
    :param cubo_id:
    :param file_path:
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
    if cubo_id and file_path and plataform_url and username and password:
        load_execution = upload_local_2_cube(
            destination_id=cubo_id,
            file_path=file_path,
            plataform_url=plataform_url,
            username=username,
            password= password,
            data_format=data_format,
            file_processing_timeout=int(timeout['file']),
            execution_parameters=execution_parameters,
            ignore_validation_errors=datainput_parameters['ignoreValidationErrors'],
        )
        
        load_execution.wait_until_finished()

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
    data_format = kwargs.get('data_format', {
        "charset": "UTF-8",
        "quote": "\"",
        "escape": "\\",
        "delimiter": ",",
    })
    filters = kwargs.get('filters', None)
    if cubo_id and cubo_name:
        raise ValueError(DOWNLOAD_ERROR_JUST_ID_OR_NAME)
    if (cubo_id or cubo_name) and plataform_url and username and password and columns and file_path:
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
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    else:
        raise ValueError(ERROR_ARGUMENTS_VALIDATION)

