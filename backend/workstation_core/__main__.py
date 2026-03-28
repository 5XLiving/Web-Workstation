from __future__ import annotations

import os

from . import create_app


def main() -> None:
    app = create_app()
    host = os.environ.get("WORKSTATION_CORE_HOST", "127.0.0.1")
    port = int(os.environ.get("WORKSTATION_CORE_PORT", "5000"))
    debug = os.environ.get("WORKSTATION_CORE_DEBUG", "true").lower() == "true"
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()