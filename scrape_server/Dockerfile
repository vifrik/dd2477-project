FROM python
COPY . /app
WORKDIR /app
RUN python3 -m pip install -r /app/requirements.txt
CMD python3 /app/scrape_server.py
EXPOSE 5001