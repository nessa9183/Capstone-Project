FROM python:2.7
LABEL developer="Shubham Kandwal"

COPY /techtrends/. /app
WORKDIR /app
RUN pip install -r requirements.txt 
RUN python init_db.py

CMD ["python", "app.py"]