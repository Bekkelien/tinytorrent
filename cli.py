import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-f', type=str, required=True)

# Parse the argument
args = parser.parse_args()

print(args.f)
