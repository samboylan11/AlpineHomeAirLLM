# Alpine Home Air LLM

> Chatbot for Alpine Home Air Learning Center.

## Introduction

Codebase that allows you to create chatbots for any webpage (Currently Specific to Alpine Home Air) and some experiental trials on ingesting all documents in file llm_sitemap_scrape.py.

## Features

- Scrape any page on Learning Center and create a Chatbot from it.
- Scrape all pages from Learning Center and create a Chatbot from it.

## Installation

```<python>
# Install required python packages
pip install -r requirements.txt

# Run uvicorn to scale and deploy API
uvicorn alpine_llm_api:app --host 0.0.0.0 --reload --port 5000
```

## Usage

https://colab.research.google.com/drive/1rOS_YtRVomUg8W3LZP2xt5WVxY3NpizX?authuser=0#scrollTo=6oclZiGTTX7_


## Credits

By: Samuel Boylan-Sajous
