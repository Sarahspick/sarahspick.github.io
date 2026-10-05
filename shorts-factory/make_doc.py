"""Render a long-form documentary:  python make_doc.py documentaries/<id>.json [--plan]"""
import sys

from factory.doc_render import render

if __name__ == "__main__":
    render(sys.argv[1], only_plan="--plan" in sys.argv)
