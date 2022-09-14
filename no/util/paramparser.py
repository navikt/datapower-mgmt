import argparse

def _parse_cli_args():
    parser = argparse.ArgumentParser(description="Python lib for DataPower management ")
    parser.add_argument(
        "-i",
        "--inventory",
        action = "store",
        dest = "inventory_list",
        type = str,
        nargs = "+",
        required = True,
        help = "DataPower hosts"
    )

    parser.add_argument(
        "--port",
        action = "store",
        type = int,
        default = 5554,
        help = "DataPower REST port. Use same port for all instances (Default 5444)"
    )

    parser.add_argument(
        "--dir",
        action = "store",
        help = "Path to directory where to store files (Default: current path)"
    )

    parser.add_argument(
        "--domain",
        action = "store",
        default = "default",
        help = "Select domain on DataPower appliance (Default domain: default)"
    )

    parser.add_argument(
        "-c"
        "--config",
        action = "store",
        dest = "config",
        help = "DataPower config file (Not in use)"
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="Send debug messages to STDERR (Default False)",
    )
    parser.add_argument(
        "-u",
        "--username",
        action="store",
        required=True,
        help="Username",
    )
    parser.add_argument(
        "-p",
        "--password",
        action="store",
        required=True,
        help="password",
    )

    parser.add_argument(
        "--ignore_ssl",
        action="store_true",
        required=False,
        help="ignore_ssl",
    )

    parser.add_argument(
        "--timeout",
        action="store",
        type=int,
        default=120,
        help="Connection timeout"
    )
    
    parser.add_argument(
        "--ilmt_destination",
        action="store",
        help="Destination for ILMT server. user@host:/path"
    )

    return parser.parse_args()