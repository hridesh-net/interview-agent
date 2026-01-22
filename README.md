# Interviewer which can see you

## Prerequisite
### Install dapr in your system (Must have docker running)
```bash
brew install dapr/tap/dapr-cli
```

```bash
dapr init
```

### Run application

```bash
uv venv
```
```bash
source .venv/bin/activate
```

```bash
uv sync
```

```bash
dapr run -f interview-run.yaml
```
```bash
dapr run -f scoring-run.yaml
```