FROM python:3.13
WORKDIR usr/app/src
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "app/main.py" ]



