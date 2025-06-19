.PHONY: install install-dev test run
.PHONY: docker-build docker-run docker-rerun docker-stop docker-clean docker-rebuild

# Local use

install:
	pip install .

install-dev:
	pip install ".[test]"

test:
	pytest tests

run:
	uvicorn src.main:app --reload

# Docker

docker-build:
	docker build -t turing-crud .

docker-run:
	docker run \
		--name turing-container \
		--add-host=host.docker.internal:host-gateway \
		-p 8114:8114 \
		-e DATABASE_URL="postgresql+psycopg://kubsu:kubsu@host.docker.internal:5432/kubsu" \
		turing-crud

docker-rerun: docker-stop docker-run
	@echo "Container restarted successfully"

docker-stop:
	-docker stop turing-container
	-docker rm turing-container

docker-clean: docker-stop
	-docker rmi turing-crud
	-docker system prune -f

docker-rebuild: docker-clean docker-build docker-run
	@echo "Full rebuild completed"