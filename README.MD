### Notes:
- used docker, Docker Desktop
- used harbor, uv

### Expectations:
```sh 
harbor run -p log-report -a oracle     # reference solution -> should PASS (reward 1)
harbor run -p log-report --agent nop   # no-op agent -> a good verifier must FAIL (reward 0)
```