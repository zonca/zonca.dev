.PHONY: list

all: pull render publish

list:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

publish:
	quarto publish gh-pages --no-prompt --no-render --no-browser

pull:
	git pull --rebase

render:
	quarto render
