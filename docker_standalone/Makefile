PACKAGE = PythonChromiumHTML2PDF
IMAGE_BASE_NAME = python-chromium-html2pdf-docker
IMAGE_TAG = $(shell git describe --tags --always --dirty)
TARGET = command

build:
	docker build \
		--target $(TARGET) \
		-t $(IMAGE_BASE_NAME):$(IMAGE_TAG) \
		-t $(IMAGE_BASE_NAME):$(IMAGE_TAG)-$(TARGET) \
		-f Dockerfile .

test: TARGET = test
test: build
	docker run $(IMAGE_BASE_NAME):$(IMAGE_TAG)-$(TARGET) nosetests -v tests

lint: TARGET = test
lint: build
	docker run $(IMAGE_BASE_NAME):$(IMAGE_TAG)-$(TARGET) flake8 command

run_file: FILE = ''
run_file: ABS_FILE = $(shell readlink -f $(FILE))
run_file: DISK_FILE_DIR = $(shell dirname $(ABS_FILE))
run_file: CONTAINER_FILE_DIR = $(shell basename $(DISK_FILE_DIR))
run_file: CONTAINER_FILE = $(CONTAINER_FILE_DIR)/$(shell basename $(ABS_FILE))
run_file: OUTPUT = result.pdf
run_file: OPTIONS = {}
run_file: TARGET = command
run_file: build
	docker rm $(IMAGE_BASE_NAME)-run_file > /dev/null 2>&1; \
	docker run \
		--name $(IMAGE_BASE_NAME)-run_file \
		-v $(DISK_FILE_DIR):/src/$(CONTAINER_FILE_DIR) \
		$(IMAGE_BASE_NAME):$(IMAGE_TAG)-$(TARGET) \
		--file=$(CONTAINER_FILE) \
		--target=/src/output.pdf \
		--options=$(OPTIONS); \
    docker cp $(IMAGE_BASE_NAME)-run_file:/src/output.pdf $(OUTPUT)

run_link: LINK = ''
run_link: OUTPUT = result.pdf
run_link: OPTIONS = {}
run_link: TARGET = command
run_link: build
	docker rm $(IMAGE_BASE_NAME)-run_link > /dev/null 2>&1; \
	docker run \
		--name $(IMAGE_BASE_NAME)-run_link \
		$(IMAGE_BASE_NAME):$(IMAGE_TAG)-$(TARGET) \
		--link=$(LINK) --target=/src/output.pdf --options=$(OPTIONS); \
    docker cp $(IMAGE_BASE_NAME)-run_link:/src/output.pdf $(OUTPUT)
