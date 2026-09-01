# satellite-lighting

A small Python (>= 3.12) service that turns office lighting into a live satellite
tracker. It watches a configured location, and whenever one of the satellites you
care about is passing overhead it emits a lighting command for each satellite and 
the corresponding color

## Command format

When one or more satellites are overhead, the service emits one line listing each
overhead satellite (in config order) and its colour:

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

A single JSON file (see `config.example.json`). `location`, `satellites` and
`outputs` are required; the `tracking` block is optional (sensible defaults are used
if omitted). Output types are `stdout`, `file` (needs `path`) and `tcp` (needs `host`
and `port`).

```json
{
  "location": {"name": "Loft Lab", "latitude": 39.7266, "longitude": -105.2064},
  "satellites": [
    {"norad_id": 25544, "color": "blue"},
    {"norad_id": 48915, "color": "pink"}
  ],
  "outputs": [
    {"type": "stdout"},
    {"type": "file", "path": "commands.log"},
    {"type": "tcp", "host": "127.0.0.1", "port": 9000}
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
