from input.collector import collect_data
from processor.processor import process_data
from output.reporter import make_report


def run(data=None):
    if data is None:
        data = collect_data()

    processed = process_data(data)
    return make_report(processed)
