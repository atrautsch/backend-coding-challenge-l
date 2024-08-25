FROM python:3.11-slim

WORKDIR /gistapi

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 9876/tcp

COPY . .

CMD [ "python3", "-m" , "flask", "--app", "gistapi/gistapi.py", "run", "--host=0.0.0.0", "--port=9876"]
