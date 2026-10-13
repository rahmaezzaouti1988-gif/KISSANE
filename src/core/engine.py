from input.collector import collect_data
from processor.processor import process_data
from output.reporter import make_report

def run():
    data = collect_data()
    processed = process_data(data)
    report = make_report(processed)
    return report
