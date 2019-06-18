.PHONY: test deploy deploy-function
.DEFAULT_GOAL := test

test:
	flake8
	pytest -sv --cov=chatless
deploy:
	serverless deploy
deploy-function:
	serverless deploy -f chatbot
#	serverless logs -f chatbot -t
