FROM python:3.7-bullseye

WORKDIR /app
RUN pip3 install bdrmapit
COPY . /app
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

ENTRYPOINT ["/bin/bash"]
