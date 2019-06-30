FROM python:3.6
COPY . /app
WORKDIR /app
ENV LISTEN_PORT=443
EXPOSE 443
RUN pip install -r requirements.txt
CMD ["waitress-serve", "--listen=0.0.0.0:443", "nn_server:app"]