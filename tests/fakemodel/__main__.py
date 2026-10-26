"""Run the invented stand-in: python -m tests.fakemodel."""

import argparse
import sys

from .core import DEFAULT_MODEL, MODES, FakeModel
from .server import serve


def main(argv=None):
    parser = argparse.ArgumentParser(description="Recorded Ollama stand-in, invented data only")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18434)
    parser.add_argument("--mode", choices=MODES, default="replay")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    try:
        server = serve(args.bind, args.port, FakeModel(mode=args.mode, model=args.model))
    except OSError as exc:
        print(f"fakemodel: {exc}", file=sys.stderr)
        return 1
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
