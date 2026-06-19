"""
InterviewGPT — PDF Report Generator

Generates styled PDF reports from interview data using HTML templates.
"""

import os
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_report_html(report_data: dict, interview_data: dict) -> str:
    """Generate styled HTML for PDF conversion."""
    grade = report_data.get("overall_grade", "N/A")
    score = report_data.get("overall_score", 0)
    
    grade_color = "#22c55e" if grade.startswith("A") else "#eab308" if grade.startswith("B") else "#ef4444"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; line-height: 1.6; padding: 40px; }}
            .header {{ text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 3px solid #2563eb; }}
            .header h1 {{ color: #2563eb; font-size: 28px; margin-bottom: 8px; }}
            .header p {{ color: #64748b; font-size: 14px; }}
            .grade-badge {{ display: inline-block; background: {grade_color}; color: white; padding: 8px 24px; border-radius: 8px; font-size: 24px; font-weight: bold; margin: 16px 0; }}
            .section {{ margin-bottom: 32px; }}
            .section h2 {{ color: #2563eb; font-size: 20px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; }}
            .section h3 {{ color: #475569; font-size: 16px; margin: 12px 0 8px; }}
            .score-bar {{ background: #e2e8f0; border-radius: 4px; height: 8px; margin: 4px 0 12px; }}
            .score-fill {{ background: #2563eb; border-radius: 4px; height: 8px; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 4px; }}
            .meta {{ display: flex; justify-content: space-between; margin-bottom: 24px; }}
            .meta-item {{ text-align: center; }}
            .meta-item .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; }}
            .meta-item .value {{ font-size: 16px; font-weight: 600; color: #1e293b; }}
            .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>InterviewGPT — Interview Report</h1>
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
            <div class="grade-badge">Grade: {grade}</div>
        </div>

        <div class="meta">
            <div class="meta-item"><div class="label">Role</div><div class="value">{interview_data.get('target_role', 'N/A')}</div></div>
            <div class="meta-item"><div class="label">Type</div><div class="value">{interview_data.get('interview_type', 'N/A').replace('_', ' ').title()}</div></div>
            <div class="meta-item"><div class="label">Score</div><div class="value">{score:.1f}/10</div></div>
            <div class="meta-item"><div class="label">Duration</div><div class="value">{interview_data.get('duration_minutes', 'N/A')} min</div></div>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <p>{report_data.get('executive_summary', 'No summary available.')}</p>
        </div>
    """

    # Technical Assessment
    tech = report_data.get("technical_assessment", {})
    if tech:
        tech_score = tech.get("score", 0)
        html += f"""
        <div class="section">
            <h2>Technical Assessment — {tech_score:.1f}/10</h2>
            <div class="score-bar"><div class="score-fill" style="width: {tech_score*10}%"></div></div>
            <p>{tech.get('summary', '')}</p>
            <div class="card">
                <h3>Key Strengths</h3>
                <ul>{''.join(f'<li>{s}</li>' for s in tech.get('key_strengths', []))}</ul>
            </div>
            <div class="card">
                <h3>Areas for Improvement</h3>
                <ul>{''.join(f'<li>{s}</li>' for s in tech.get('areas_for_improvement', []))}</ul>
            </div>
        </div>
        """

    # Improvement Areas
    improvements = report_data.get("improvement_areas", [])
    if improvements:
        html += """<div class="section"><h2>Improvement Areas</h2>"""
        for item in improvements:
            if isinstance(item, dict):
                html += f"""<div class="card"><h3>{item.get('area', 'General')}</h3><p>{item.get('recommendation', '')}</p></div>"""
        html += "</div>"

    # Learning Path
    learning = report_data.get("learning_path", [])
    if learning:
        html += """<div class="section"><h2>Suggested Learning Path</h2>"""
        for item in learning:
            if isinstance(item, dict):
                html += f"""<div class="card"><h3>{item.get('topic', '')}</h3><p>{item.get('description', '')}</p></div>"""
        html += "</div>"

    html += """
        <div class="footer">
            <p>Generated by InterviewGPT — AI-Powered Mock Interview Platform</p>
        </div>
    </body>
    </html>
    """
    return html


async def generate_pdf_report(report_data: dict, interview_data: dict, output_dir: str = "./reports") -> str:
    """Generate a PDF report and return the file path."""
    os.makedirs(output_dir, exist_ok=True)
    
    html_content = generate_report_html(report_data, interview_data)
    pdf_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(pdf_path)
        logger.info(f"PDF report generated: {pdf_path}")
    except ImportError:
        logger.warning("WeasyPrint not installed, saving HTML instead")
        pdf_path = pdf_path.replace(".pdf", ".html")
        with open(pdf_path, "w") as f:
            f.write(html_content)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        pdf_path = pdf_path.replace(".pdf", ".html")
        with open(pdf_path, "w") as f:
            f.write(html_content)

    return pdf_path
