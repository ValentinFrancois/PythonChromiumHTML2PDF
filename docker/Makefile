MAKEFLAGS =+ -rR --warn-undefined-variables

PACKAGE = PythonChromiumHTML2PDF
IMAGE_BASE_NAME = python-chromium-html2pdf/standalone
IMAGE_TAG = $(shell git describe --tags --always --dirty)

build:
	docker build -t $(IMAGE_BASE_NAME):$(IMAGE_TAG) -f Dockerfile ..

test:
	docker run $(IMAGE_BASE_NAME):$(IMAGE_TAG) \
		nosetests -v --with-coverage --cover-package=$(PACKAGE) tests

lint:
	docker run $(IMAGE_BASE_NAME):$(IMAGE_TAG) \
		flake8 $(PACKAGE)

bandit:
	docker run $(IMAGE_BASE_NAME):$(IMAGE_TAG) \
		bandit -r $(PACKAGE)
