VERSION := $(shell git describe --abbrev=0 --tags 2> /dev/null )
ifeq ($(VERSION),)
  VERSION := latest
endif

ARCH := $(shell uname -m | sed s/aarch64/arm64/ | sed s/x86_64/amd64/)

create-venv:
	python -m venv .venv

activate-venv:
	source .venv/bin/activate

build-requirements:
	pip-compile -o requirements.txt pyproject.toml

build-requirements-dev:
	pip-compile --extra dev -o requirements-dev.txt pyproject.toml --allow-unsafe

dev:
	python src/main.py

requirements-dev:
	python -m pip install -r requirements-dev.txt

requirements:
	pip-sync requirements.txt requirements-dev.txt

docker-build:
	docker build -t ghcr.io/defenseunicorns/leapfrogai/rag:${VERSION} . --build-arg ARCH=${ARCH}

docker-build-local-registry:
	if [ -f .env ]; then \
		echo "env file exists"; \
	else \
		echo "env file does not exist, using .env.example."; \
		cp .env.example .env; \
	fi
	docker build -t ghcr.io/defenseunicorns/leapfrogai/rag:${VERSION} .
	docker tag ghcr.io/defenseunicorns/leapfrogai/rag:${VERSION} localhost:5000/defenseunicorns/leapfrogai/rag:${VERSION}
	docker push localhost:5000/defenseunicorns/leapfrogai/rag:${VERSION}

docker-release:
	docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/defenseunicorns/leapfrogai/rag:${VERSION} --push .

docker-run:
	mkdir -p db
	if [ -f .env ]; then \
		echo "env file exists"; \
	else \
		echo "env file does not exist, using .env.example."; \
		cp .env.example .env; \
	fi
	docker run -p 8000:8000 -v ./db/:/leapfrogai/db/ -d --env-file .env ghcr.io/defenseunicorns/leapfrogai/rag:${VERSION}

test:
	pytest tests/test_main.py

zarf-create:
	zarf package create . --confirm --set=PACKAGE_VERSION=${VERSION} --set=IMAGE_VERSION=${VERSION}

zarf-create-local-registry:
	zarf package create . --confirm --registry-override ghcr.io=localhost:5000 --set IMG=defenseunicorns/leapfrogai/rag:${VERSION}

zarf-deploy:
	zarf package deploy --confirm zarf-package-*.tar.zst

zarf-publish:
	zarf package publish zarf-*.tar.zst oci://ghcr.io/defenseunicorns/leapfrogai/packages/
