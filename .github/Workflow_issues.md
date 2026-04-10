# List of issues to address before new pipline deployement


Issues Pipeline:

- [x] Actions label not user(or dev) friendly 
- [x] Label stable -> staging
- [ ] issues on .yml files
    - [ ] Environment does not exist issues:
    - [ ] step_docker-image.yml: dockerhub
    - [ ] step_testpypi_release.yml: testpypi
    - [ ] step_pypi_release.yml: pypi
- [X] Create Git secret 
    - [X] TEST_PYPI_API_TOKEN -> created on testpypi, an organization request has been made on testpypi as well.
- [ ] Modify the pipeline:
    - [ ] On master: replace Make doc by step_publish_stable_docs
    - [ ] On Staging: add step_prebuild_docs before pip testpypi version
- [ ] 
