import io
import zipfile

import requests


def download_nnue_from_stockfish(url: str):
    pass


def download_file_from_google_drive(id: str) -> io.BytesIO:
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                destination.write(chunk)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    zipdata = io.BytesIO()
    save_response_content(response, zipdata)
    return zipfile.ZipFile(zipdata).open("all_with_filtered_anotations_since1998.txt")
