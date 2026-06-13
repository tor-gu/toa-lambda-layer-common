.PHONY: build clean

ZIP_NAME := common.zip

build: clean
	zip -r $(ZIP_NAME) python/
	@echo "Built $(ZIP_NAME)"

clean:
	rm -f $(ZIP_NAME)
