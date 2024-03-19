import argparse
import os
from pathlib import Path
from zipfile import ZipFile
import termcolor
from fastapi import UploadFile
import requests
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made.")

RED = "red"
GREEN = "green"
YELLOW = "yellow"
BLUE = "blue"
WHITE = "white"
COLLECTION_NAME_HELP_MESSAGE = "(REQUIRED) Name of the collection you want to attach your file to."
SUPPORTED_FILE_TYPES = [".zip", ".txt", ".pdf"]
SUPPORTED_FILE_TYPE_MESSAGE = F"Supported file types are: {", ".join(SUPPORTED_FILE_TYPES)}"
FILE_HELP_MESSAGE = f"(REQUIRED)Path to the file that you want to upload to the RAG. {SUPPORTED_FILE_TYPE_MESSAGE}"
URL_HELP_MESSAGE = "URL to the rag you want to upload to."


def printError(text):
    printRed(f"ERROR: {text}")

def printRed(text):
    print(termcolor.colored(text, RED))

def printGreen(text):
    print(termcolor.colored(text, GREEN))

def printYellow(text):
    print(termcolor.colored(text, YELLOW))

def printBlue(text):
    print(termcolor.colored(text, BLUE))

def printMulti(tuples, between=""):    
    for text, color in tuples:
        print(termcolor.colored(text, color), end=between)
    print()

def setupParser():
    parser = argparse.ArgumentParser(description="Upload files to da RAG")
    parser.add_argument("--collection_name", "-c", type=str, help=COLLECTION_NAME_HELP_MESSAGE, required=True)
    parser.add_argument("--file", "-f", type=str, help=FILE_HELP_MESSAGE, required=True)
    parser.add_argument("--url", "-u", type=str, help=URL_HELP_MESSAGE)
    return parser

def getArgs():
    parser = setupParser()
    args = parser.parse_args()

    collection_name = args.collection_name
    file_name = args.file
    rag_url = args.url

    file_path = Path(file_name)
    file_extension = file_path.suffix.lower()

    if file_extension not in [".zip", ".txt", ".pdf"]:
        printError(f"File type not supported. {SUPPORTED_FILE_TYPE_MESSAGE}")
        exit()

    printMulti([("Collection Name: ", BLUE), (collection_name, YELLOW)])
    printMulti([("File Path: ", BLUE), (file_path, YELLOW)])

    # if the rag url isn't set then attempt to get it from the environment
    if rag_url is not None:
        printMulti([("RAG_URL: ", BLUE), (rag_url, YELLOW)])
    else:
        rag_url = os.getenv("RAG_URL")

        if rag_url is None:
            printError("RAG_URL environment variable is not set and --url, -u option not set.")
        else:
            printMulti([("RAG_URL: ", BLUE), (rag_url, YELLOW)])

    return collection_name, file_name, rag_url

def uploadFile(collection_name, file_name, rag_url):
    # form thet api request
    uploadUrlWithQuery = f"{rag_url}/upload/?collection_name={collection_name}"
    file = open(file_name, "rb")
    form_data = { "file": ("swarm.pdf", file )}
    try:
        # Send the POST request
        response = requests.post(uploadUrlWithQuery, files=form_data, verify=False)

        if (response.status_code == 200):
            printGreen("Successful request to upload file to RAG")
    except requests.exceptions.RequestException as e:
        printError(f"Error sending POST request: {str(e)}")

def verifyFileUpload(collection_name, rag_url):
    data = { 
          "input": "List some key points from the documents.",
          "collection_name": collection_name 
      }

    try:
        response = requests.post(f"{rag_url}/query/raw", json=data, verify=False)

        if (response.status_code == 200):
            printGreen("Verified file was added to collection")
    except requests.exceptions.RequestException as e:
        printError(f"Error sending POST request: {str(e)}")

    
def main():
    collection_name, file_name, rag_url = getArgs()

    uploadFile(collection_name, file_name, rag_url)

    printBlue("Verifiying that file was added to collection...")

    verifyFileUpload(collection_name, rag_url)

    printBlue("Exiting RAG Uploader CLI")

if __name__ == "__main__":
    main()