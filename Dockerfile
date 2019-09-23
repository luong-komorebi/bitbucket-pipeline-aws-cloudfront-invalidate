FROM python:3.7-slim

# install requirements
COPY requirements.txt /usr/bin
WORKDIR /usr/bin
RUN pip install -r requirements.txt

# copy the pipe source code
COPY pipe.py pipe.yml /usr/bin/

ENTRYPOINT ["python3", "/usr/bin/pipe.py"]