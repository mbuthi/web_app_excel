import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class SheetyApi:
    def __init__(self,
                 family, genus,
                 species, authority,
                 localName, language,
                 size_file, country, scribe, size_tiff):
        self.url = os.getenv("SHEET_ENDPOINT")
        self.response = ""
        self.data_length = 1
        self.size_tiff = size_tiff

        self.parameters = {
            "pdfCamp": {
                "cardNumber": self.data_length,
                "family": family,
                "genus": genus,
                "species": species,
                "authority": authority,
                "localName": localName,
                "language": language,
                "medicinalValue": "Not Recorded",
                "otherUsage": "Not Recorded",
                "typeOfFile": "PDF",
                "imageFormat": "Black and White",
                "sizeOfFile": f"{size_file}KB",
                "numberOfPages": 1,
                "originalFormat": "Card",
                "typeOfContent": "Text",
                "country": country,
                "scribe": scribe,
                "entryDate": datetime.datetime.now().strftime("%d/%b/%Y"),
                "validation": "",
            }
        }

    def post_data(self):
        token = os.getenv("BEARER_TOKEN")
        auth_token = {
            "Authorization": f"Bearer {token}"
        }
        data_length__ = 0
        try:
            data_length__ = requests.get(self.url, headers=auth_token).json()["pdfCamp"][-2]["cardNumber"]

        except IndexError:
            data_length__ = 0
        for i in range(0, 2):

            data_length_ = data_length__ + 1
            self.parameters["pdfCamp"]["cardNumber"] = data_length_

            if i == 1:
                self.parameters["pdfCamp"]["typeOfFile"] = "TIFF"
                self.parameters["pdfCamp"]["cardNumber"] = ""
                self.parameters["pdfCamp"]["sizeOfFile"] = f"{self.size_tiff}KB"
            self.response = requests.post(url=self.url, json=self.parameters, headers=auth_token)
