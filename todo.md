# Before minor release v 1.4.0.

- [ ] Validate full pipeline
- [ ] Delete _bckp/* !!! Bring back tuto and exemple before
- [ ] Clean branches
    - [ ] ``dev``:
        - [ ] Generated tuto/examples in doc
        - [ ] recreated bash_nrv file
    - [ ] ``staging``:
        - [ ] remove ./tests (unitary_tests)
    - [ ] ``master``
        - [ ] remove ./tests (unitary_tests)
- [ ] clean test folders hierarchy
    - [ ] tests
            |
             - unit 
                | nrv ...
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
- [ ] Set ``dev``-branch as default
- [ ] Complementary actions
    - [ ] clean tags (in case of issues)
    - [ ] Build/publish ``dev`` doc
    - [ ] Zenodo link in Readme.md
- [ ] GitHub rule set
    - [ ] automatization of merge requests
        - [ ] ``dev`` -> ``staging``
        - [ ] ``staging`` -> ``master``
    - [ ] writing authorisations:
        - [ ] Forbid for user and NRV-team on ``staging`` and ``master``
        - [ ] Forbid for user on ``dev``
- [ ] Code
    - [ ] add get/print machine config and sim parameters
        - [ ] implement
        - [ ] add to all exemples/tuto