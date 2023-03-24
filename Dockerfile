FROM python:alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY ./requirements-real.txt /app/requirements-real.txt
RUN pip install -r requirements-real.txt
COPY . /app
RUN chmod +x ./start.sh
RUN pytest
RUN touch /app/keyval.db
CMD ["/bin/sh" , "./start.sh"]
