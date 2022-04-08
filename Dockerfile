FROM python:alpine
COPY . /app
WORKDIR /app
RUN pip install -r requirements-real.txt && chmod +x ./start.sh
CMD ["/bin/sh" , "./start.sh"]
