IMAGE_NAME=ns_tester_vnc
CONTAINER_NAME=ns_tester_vnc_run
LOCAL_PORT=5901
CONTAINER_PORT=5901
SOURCE_DIR=$(shell pwd)

rebuild: clean-venv docker-build docker-run

clean-venv:
	@echo "🧹 Removing local venv..."
	rm -rf venv

docker-build:
	@echo "🐳 Building Docker image..."
	docker build --no-cache -t $(IMAGE_NAME) .

docker-run:
	@echo "🚀 Running Docker container with VNC and mounted source..."
	docker run -it --rm \
		-p $(LOCAL_PORT):$(CONTAINER_PORT) \
		-e START_VNC=1 \
		-v $(SOURCE_DIR):/app \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME) & \
	sleep 3 && open vnc://localhost:$(LOCAL_PORT)
