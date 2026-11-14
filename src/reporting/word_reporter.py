
from pathlib import Path
from datetime import datetime

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import (
    WD_TABLE_ALIGNMENT,
    WD_CELL_VERTICAL_ALIGNMENT
)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class WordReporter:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.screenshot_folder = (
            self.project_root / "reports" / "screenshots"
        )

        self.report_folder = self.project_root / "reports"

        self.report_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    # --------------------------------------------------
    # TABLE CELL FORMATTING
    # --------------------------------------------------

    def set_cell_shading(self, cell, fill):

        shading = OxmlElement("w:shd")
        shading.set(qn("w:fill"), fill)

        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(self, cell):

        tc = cell._tc
        tc_pr = tc.get_or_add_tcPr()

        margins = OxmlElement("w:tcMar")

        for margin in ["top", "start", "bottom", "end"]:

            node = OxmlElement(f"w:{margin}")
            node.set(qn("w:w"), "100")
            node.set(qn("w:type"), "dxa")

            margins.append(node)

        tc_pr.append(margins)

    def format_cell(
        self,
        cell,
        text,
        bold=False,
        color=None,
        font_size=10
    ):

        cell.text = str(text)

        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

        self.set_cell_margins(cell)

        for paragraph in cell.paragraphs:

            paragraph.paragraph_format.space_after = Pt(3)
            paragraph.paragraph_format.space_before = Pt(3)

            for run in paragraph.runs:

                run.bold = bold
                run.font.size = Pt(font_size)

                if color:
                    run.font.color.rgb = RGBColor(*color)

    def format_table(self, table):

        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

    # --------------------------------------------------
    # SUMMARY TABLE
    # --------------------------------------------------

    def add_summary_table(
        self,
        document,
        total,
        passed,
        failed
    ):

        table = document.add_table(
            rows=2,
            cols=3
        )

        self.format_table(table)

        headers = [
            "Total Tests",
            "Passed",
            "Failed"
        ]

        values = [
            str(total),
            str(passed),
            str(failed)
        ]

        for index in range(3):

            header_cell = table.rows[0].cells[index]

            self.format_cell(
                header_cell,
                headers[index],
                bold=True,
                color=(255, 255, 255),
                font_size=11
            )

            self.set_cell_shading(
                header_cell,
                "1F4E78"
            )

            value_cell = table.rows[1].cells[index]

            self.format_cell(
                value_cell,
                values[index],
                bold=True,
                font_size=14
            )

            value_cell.paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

        document.add_paragraph()

    # --------------------------------------------------
    # TEST CASE DETAILS TABLE
    # --------------------------------------------------

    def add_test_details_table(self, document, case):

        table = document.add_table(
            rows=0,
            cols=2
        )

        self.format_table(table)

        fields = [
            ("Test Case ID", case.get("id", "Not assigned")),
            ("Scenario", case.get("scenario", "Not specified")),
            ("Expected Result", case.get("expected", "Not specified")),
            ("Actual Result", case.get("actual", "Not specified")),
            ("Execution Status", case.get("status", "Not recorded")),
        ]

        for label, value in fields:

            cells = table.add_row().cells

            self.format_cell(
                cells[0],
                label,
                bold=True,
                font_size=9
            )

            self.set_cell_shading(
                cells[0],
                "D9EAF7"
            )

            self.format_cell(
                cells[1],
                value,
                font_size=9
            )

        if table.rows:

            for row in table.rows:

                row.cells[0].width = Inches(1.65)
                row.cells[1].width = Inches(5.65)

        document.add_paragraph()

    # --------------------------------------------------
    # EXECUTION STEP
    # --------------------------------------------------

    def add_execution_step(
        self,
        document,
        step_number,
        step
    ):

        description = step.get(
            "description",
            "Execution Step"
        )

        heading = document.add_heading(
            f"Step {step_number}: {description}",
            level=3
        )

        heading.paragraph_format.space_before = Pt(12)
        heading.paragraph_format.space_after = Pt(5)

        expected_paragraph = document.add_paragraph()

        expected_run = expected_paragraph.add_run("Expected: ")
        expected_run.bold = True

        expected_paragraph.add_run(
            step.get("expected", "Not specified")
        )

        actual_paragraph = document.add_paragraph()

        actual_run = actual_paragraph.add_run("Actual: ")
        actual_run.bold = True

        actual_paragraph.add_run(
            step.get("actual", "Not recorded")
        )

        screenshot = step.get("screenshot")

        if screenshot:

            screenshot_path = Path(screenshot)

            if not screenshot_path.is_absolute():

                screenshot_path = (
                    self.screenshot_folder / screenshot_path
                )

            if screenshot_path.exists():

                image_paragraph = document.add_paragraph()

                image_paragraph.alignment = (
                    WD_ALIGN_PARAGRAPH.CENTER
                )

                image_paragraph.paragraph_format.space_before = Pt(5)

                image_paragraph.add_run().add_picture(
                    str(screenshot_path),
                    width=Inches(5.8)
                )

                caption = document.add_paragraph()

                caption.alignment = (
                    WD_ALIGN_PARAGRAPH.CENTER
                )

                caption.paragraph_format.space_after = Pt(10)

                caption_run = caption.add_run(
                    "Evidence: "
                    + step.get(
                        "evidence_label",
                        description
                    )
                )

                caption_run.italic = True
                caption_run.font.size = Pt(9)
                caption_run.font.color.rgb = RGBColor(
                    100,
                    100,
                    100
                )

            else:

                document.add_paragraph(
                    f"Screenshot not found: {screenshot_path.name}"
                )

        else:

            document.add_paragraph(
                "No screenshot attached for this step."
            )

    # --------------------------------------------------
    # MAIN REPORT GENERATION
    # --------------------------------------------------

    def generate_report(
        self,
        report_title,
        test_cases,
        report_name="SauceDemo_Execution_Report"
    ):

        document = Document()

        # Document margins
        section = document.sections[0]

        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

        # Default font
        normal_style = document.styles["Normal"]

        normal_style.font.name = "Arial"
        normal_style.font.size = Pt(10)

        # Main title
        title = document.add_heading(
            report_title,
            level=0
        )

        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        for run in title.runs:

            run.font.color.rgb = RGBColor(
                31,
                78,
                121
            )

        # Subtitle
        subtitle = document.add_paragraph()

        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

        subtitle_run = subtitle.add_run(
            "Customer Test Execution Report"
        )

        subtitle_run.bold = True
        subtitle_run.font.size = Pt(12)

        # Execution information
        document.add_paragraph(
            f"Execution Date: "
            f"{datetime.now().strftime('%d %B %Y, %H:%M:%S')}"
        )

        document.add_paragraph(
            "Application: SauceDemo"
        )

        document.add_paragraph(
            "Automation Tool: Python + Playwright"
        )

        # --------------------------------------------------
        # EXECUTION SUMMARY
        # --------------------------------------------------

        document.add_heading(
            "1. Execution Summary",
            level=1
        )

        total = len(test_cases)

        passed = sum(
            1 for case in test_cases
            if case.get("status", "").upper() == "PASS"
        )

        failed = sum(
            1 for case in test_cases
            if case.get("status", "").upper() == "FAIL"
        )

        self.add_summary_table(
            document,
            total,
            passed,
            failed
        )

        # --------------------------------------------------
        # DETAILED TEST EXECUTION
        # --------------------------------------------------

        document.add_heading(
            "2. Detailed Test Execution",
            level=1
        )

        for case_number, case in enumerate(
            test_cases,
            start=1
        ):

            document.add_heading(
                f"Test Case {case_number}: "
                f"{case.get('title', 'Untitled Test')}",
                level=2
            )

            # Test case details
            self.add_test_details_table(
                document,
                case
            )

            # Execution steps
            document.add_heading(
                "Execution Steps",
                level=2
            )

            steps = case.get("steps", [])

            if not steps:

                document.add_paragraph(
                    "No execution steps recorded."
                )

            for step_number, step in enumerate(
                steps,
                start=1
            ):

                self.add_execution_step(
                    document,
                    step_number,
                    step
                )

            # Failure details
            failure = case.get("failure", "")

            if failure:

                document.add_heading(
                    "Failure Details",
                    level=3
                )

                document.add_paragraph(
                    str(failure)
                )

            document.add_paragraph()

        # --------------------------------------------------
        # FOOTER
        # --------------------------------------------------

        for section in document.sections:

            footer = section.footer.paragraphs[0]

            footer.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

            footer_run = footer.add_run(
                "Confidential - Customer Test Execution Report"
            )

            footer_run.italic = True
            footer_run.font.size = Pt(8)
            footer_run.font.color.rgb = RGBColor(
                100,
                100,
                100
            )

        # --------------------------------------------------
        # SAVE REPORT
        # --------------------------------------------------

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output_path = (
            self.report_folder
            / f"{report_name}_{timestamp}.docx"
        )

        document.save(output_path)

        print(
            f"\nWord report generated: {output_path}"
        )

        return output_path
