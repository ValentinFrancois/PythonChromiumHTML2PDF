# needs build context to be the 'package' directory
# i.e. 'PythonChromiumHTML2PDF' and 'tests' are subdirectories

FROM python:3.8-slim as test

RUN apt-get update

# install chrome
RUN apt-get install -qqy chromium --no-install-recommends

# install dev linux dependencies
RUN devDependencies='procps git' \
    && apt-get install -qqy $devDependencies --no-install-recommends

WORKDIR /tests

# install dev python dependencies
COPY tests/requirements.txt test_requirements.txt
RUN pip3 install -r test_requirements.txt

# install runtime dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY PythonChromiumHTML2PDF PythonChromiumHTML2PDF

COPY tests tests
CMD ["nosetests"]
