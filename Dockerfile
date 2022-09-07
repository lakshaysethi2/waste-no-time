FROM python:alpine
COPY . /app
WORKDIR /app
RUN pip install --root-user-action=ignore -r requirements-real.txt && chmod +x ./start.sh
CMD ["/bin/sh" , "./start.sh"]
