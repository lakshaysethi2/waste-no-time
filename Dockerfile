FROM python:alpine
COPY . /app
WORKDIR /app
RUN pip install -r requirements-real.txt
CMD ["python","/app/main.py"]