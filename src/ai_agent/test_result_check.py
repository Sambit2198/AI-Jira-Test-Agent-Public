
import json
from pathlib import Path

from src.reporting.result_adapter import adapt_ai_report
from src.reporting.excel_reporter import ExcelReporter


report_path = Path("reports/ai_execution_report.json")

with report_path.open("r", encoding="utf-8") as file:
    ai_report = json.load(file)


adapted_results = adapt_ai_report(ai_report)

excel_reporter = ExcelReporter(module="AI_Generated")

for result in adapted_results:
    excel_reporter.add_result(result)


generated_file = excel_reporter.generate_report()

print("\nAI EXCEL REPORT CHECK")
print("=" * 50)
print("Total tests:", len(adapted_results))
print("Excel report:", generated_file)
print("Excel report generated successfully.")
print("=" * 50)
