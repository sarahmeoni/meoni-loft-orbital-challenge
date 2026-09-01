# satellite-lighting

A small Python (>= 3.12) service that turns office lighting into a live satellite
tracker. It watches a configured location, and whenever one of the satellites you
care about is passing overhead it emits a lighting command for each satellite and 
the corresponding color.

## Command format

When one or more satellites are overhead, the service emits one line listing each
overhead satellite (in config order) and its color:

```
25544: blue, 48915: pink
```

While nothing is overhead, nothing is emitted.

## How it works

Every `poll_interval_seconds`, the service asks the tracker which satellites are
overhead, maps those ids to colors, and sends the command to the configured
outputs. Pass windows are fetched from [satellites.fly.dev](https://satellites.fly.dev)
once and cached. The cache refreshes hourly or when its windows run out.

## Configuration

A single JSON file (see `config.example.json`). `location` and `satellites` are
required; `outputs` and `tracking` are optional. If `outputs` is omitted it defaults
to a single `stdout` sink. Output types are `stdout`, `file` (needs `path`) and `tcp`
(needs `host` and `port`).

```json
{
  "location": {"name": "Loft Lab", "latitude": 39.7266, "longitude": -105.2064},
  "satellites": [
    {"norad_id": 25544, "color": "blue"},
    {"norad_id": 48915, "color": "pink"}
  ]
}
```

## Running it

Requires Python 3.12+.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py --config config.example.json
```

Logs go to STDERR, commands to STDOUT. Stop with `Ctrl-C`. Or run in Docker:

```bash
docker build --target prod -t satellite-lighting .
docker run --rm -v "$PWD/config.example.json:/app/config.json:ro" satellite-lighting
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

## AI Usage
I used AI (Augment) to transform my util functions that validate/parse 
objects needed in this project into pydantic validation.
Augment also helped in creating tests, debugging code, and setting up the 
main and service files.
