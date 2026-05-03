# 


## Before minor release v 1.4.0.

- [X] Validate full pipeline - Github
- [x] Delete _bckp/* !!! Bring back tuto and exemple before
- [x] clean test folders hierarchy - TC
    - [x] tests
            |
             - unit 
            |
            - e2e
            |
            - deployment
            |
            - science
                |
                - untary_tests
                |
                NRV_tests
    - [x] update corresponding actions .yaml
- [x] Set ``dev``-branch as default - FK
- [x] GitHub rule set - TC
    - [x] writing authorisations:
        - [x] Forbid for user and NRV-team on ``staging`` and ``master``
        - [x] Forbid for user on ``dev``

## After minor release v 1.4.0. (patches)

- [ ] clean test folders hierarchy
             - unit 
                | nrv ...
- [ ] Complementary actions
    - [ ] clean tags (in case of issues)
    - [ ] Build/publish ``dev`` doc
    - [x] Zenodo link in Readme.md
- [ ] Code
    - [x] add get/print machine config and sim parameters
        - [x] implement
        - [ ] add to all exemples/tuto
- [ ] Clean branches
    - [ ] ``dev``:
        - [ ] Generated tuto/examples in doc
        - [ ] recreated bash_nrv file
    - [ ] ``staging``:
        - [ ] remove ./tests/science (unitary_tests)
    - [ ] ``master``
        - [ ] remove ./tests/science (unitary_tests)
- [ ] GitHub rule set
    - [ ] automatization of merge requests
        - [ ] ``dev`` -> ``staging``
        - [ ] ``staging`` -> ``master``