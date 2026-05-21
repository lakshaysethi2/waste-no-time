FROM python:alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY ./requirements-real.txt /app/requirements-real.txt
RUN pip install -r requirements-real.txt
CMD ["/bin/sh" , "./start.sh"]
