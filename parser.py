import argparse

parser = argparse.ArgumentParser(description="Microservice for uploading archive")
parser.add_argument("--delay", dest="delay", default=0,
                    help="Response delay between chunks, default to 0")
parser.add_argument("--log", dest="log", default=False,
                    help="Enable web servers debug log, default to false")
parser.add_argument("--path_to_photos", dest="path_to_photos", default="test_photos",
                    help="Response delay between chunks, default to 0")
