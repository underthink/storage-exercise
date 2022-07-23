# Build the actual application image with only what's needed to run
# the application...
FROM python:3.10-slim AS application_image

WORKDIR /opt/app
COPY src /opt/app/src
COPY data /data

VOLUME /data

CMD ["python", "-m", "src", \
    "--output", "/data/storage_asof_20200114.csv", \
    "--movements", "/data/cargo_movements.csv", \
    "--opening-balances", "/data/storage_asof_20200101.csv"]

# ...and a test image that extends the application one, with tests included and
# a different command to run the unittest command
FROM application_image AS test_image

COPY tests /opt/app/tests

CMD ["python", "-m", "unittest"]
