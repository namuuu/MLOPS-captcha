all: install run

install:
	npm run install
	pip install pillow
	pip install transformers
	pip install torch
	pip install datasets
	pip install transformers[torch]

run:
	npm run loop
	python3 ./OCR/train.py