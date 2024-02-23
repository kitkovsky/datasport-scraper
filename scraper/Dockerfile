FROM python:3.11

RUN apt-get update
RUN apt-get install -y wget

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

RUN wget https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.184/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip

WORKDIR /app
COPY scraper scraper
COPY db db

RUN mv /chromedriver-linux64/chromedriver scraper/

RUN pip install --no-cache-dir -r scraper/requirements.txt
RUN pip install --no-cache-dir -r db/requirements.txt

WORKDIR /app/scraper

CMD exec python main.py
