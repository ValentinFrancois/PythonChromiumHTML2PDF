PACKAGE = PythonChromiumHTML2PDF
IMAGE_BASE_NAME = python-chromium-html2pdf-tests
IMAGE_TAG = $(shell git describe --tags --always --dirty)

build:
	docker build -t $(IMAGE_BASE_NAME):$(IMAGE_TAG) -f tests/Dockerfile .

test: build
	docker run $(IMAGE_BASE_NAME):$(IMAGE_TAG) \
		nosetests -v --with-coverage --cover-package=$(PACKAGE) tests

lint: build
	docker run $(IMAGE_BASE_NAME):$(IMAGE_TAG) flake8 $(PACKAGE)

bandit: build
	docker run $(IMAGE_BASE_NAME):$(IMAGE_TAG) bandit -r $(PACKAGE)
