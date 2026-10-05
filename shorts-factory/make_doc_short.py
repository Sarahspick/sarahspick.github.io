"""Cut a vertical Short from a rendered documentary:  python make_doc_short.py documentaries/<id>.json <name>"""
import sys

from factory.doc_short import make

if __name__ == "__main__":
    for name in sys.argv[2:]:
        make(sys.argv[1], name)
