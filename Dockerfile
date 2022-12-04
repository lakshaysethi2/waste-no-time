FROM python:alpine
WORKDIR /app
COPY ./requirements-real.txt /app/requirements-real.txt
RUN pip install -r requirements-real.txt
COPY . /app
RUN chmod +x ./start.sh
CMD ["/bin/sh" , "./start.sh"]
