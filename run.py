from app import run_app
from sys import exit, exc_info, argv

try:
    run_app(argv)
except Exception:
    print(exc_info()[1])
    print('Error runtime: please, help us improve by reporting to us on :')
    print("\n\thttps://c-cut.github.io/")
    exit(0)