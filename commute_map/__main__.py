import argparse
import json
from pathlib import Path
from .app import run, export
from .server import serve

def main():
    parser = argparse.ArgumentParser(description="Commute Lab · synthetic algorithm MVP")
    sub = parser.add_subparsers(dest="command",required=True)
    web = sub.add_parser("serve",help="Open a local interactive demo")
    web.add_argument("--port",type=int,default=8080)
    for command in ("demo","export"):
        cmd = sub.add_parser(command)
        cmd.add_argument("--threshold",type=float,default=45)
        cmd.add_argument("--direction",choices=["home_to_work","work_to_home"],default="work_to_home")
        cmd.add_argument("--period",choices=["example","morning","evening"],default="example")
        cmd.add_argument("--buffer",type=float,default=0.2,help="Assumed extra minutes per routed km")
        cmd.add_argument("--condo",type=float,default=5)
        cmd.add_argument("--size",type=int,default=32)
        cmd.add_argument("--method",choices=["full","uniform","adaptive"],default="full")
        cmd.add_argument("--budget",type=int)
        cmd.add_argument("--output",type=Path)
    args = parser.parse_args()
    if args.command == "serve":
        try:
            serve(args.port)
        except (OSError,OverflowError) as error:
            parser.exit(2,f"Cannot start local server: {error}\n")
        return
    try:
        config = {"threshold":args.threshold,"direction":args.direction,"period":args.period,
                  "buffer_min_per_km":args.buffer,"condo_minutes":args.condo,
                  "size":args.size,"method":args.method,"budget":args.budget}
        result = export(config) if args.command == "export" else run(config)
        encoded = json.dumps(result,indent=2,allow_nan=False)+"\n"
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(encoded,encoding="utf-8")
            print(f"Saved {args.output}")
        else:
            print(encoded,end="")
    except (ValueError,OSError) as error:
        parser.exit(2,f"Invalid run: {error}\n")

if __name__ == "__main__":
    main()
