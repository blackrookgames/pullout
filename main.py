import sys

from pathlib import Path

import src.app as app
import src.boacon as boacon
import src.helper as helper

class TestObject(app.AppObject):
    def _update(self, params: app.AppUpdate):
        super()._update(params)
        if params.key == 0x20:
            app.console().print("SPACE BAR")

def main():
    if len(sys.argv) == 0: return 1
    try:
        params = app.AppStart()
        params.apipath = Path(sys.argv[0]).resolve()\
            .parent\
            .joinpath("secret")\
            .joinpath("cdp_api_key.json")
        params.objects.append(TestObject())
        app.run(params)
    except helper.CLIError as _e:
        print(f"ERROR: {_e}", file = sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())