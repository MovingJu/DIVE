port?=8080

platform=linux/arm64,linux/amd64#,linux/arm/v7
docker_img_tag=dive_server

.PHONY: build run test
docker-build:
	docker buildx build \
		--platform  $(platform) \
		-t movingju/test:$(docker_img_tag) \
		.

docker-test:
	docker build \
	-t movingju/test:$(docker_img_tag)\
	.

docker-run:
	docker run -p $(port):8000 movingju/test:$(docker_img_tag)

docker-push:
	docker push movingju/test:$(docker_img_tag)

build:

run: 
	uvicorn main:app --reload

test: 
	uv run test/main.py