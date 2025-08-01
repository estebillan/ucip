# ReportLab PDF Generation Comprehensive Guide

## Overview
ReportLab is a Python library for generating PDF documents programmatically, with support for charts, tables, complex layouts, and business reports.

## Installation:
```bash
pip install reportlab
```

## Basic Document Creation:
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_simple_pdf():
    c = canvas.Canvas("example.pdf", pagesize=letter)
    c.drawString(100, 750, "Hello World")
    c.save()
```

## Platypus Framework (Advanced Layout):
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

doc = SimpleDocTemplate("advanced.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Business Report", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body_text = "This is the report content..."
body = Paragraph(body_text, styles['Normal'])
story.append(body)

doc.build(story)
```

## Tables:
```python
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

data = [
    ['Name', 'Age', 'Country'],
    ['John', '30', 'USA'],
    ['Jane', '25', 'UK']
]

table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
```

## Charts:
```python
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.shapes import Drawing

drawing = Drawing(400, 200)
chart = HorizontalLineChart()
chart.x = 50
chart.y = 50
chart.height = 125
chart.width = 300
chart.data = [
    [13, 5, 20, 22, 37, 45, 19, 4],
    [5, 20, 46, 38, 23, 21, 6, 14]
]
drawing.add(chart)
```

## Professional Styling:
```python
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

custom_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.darkblue,
    alignment=TA_CENTER,
    spaceAfter=30
)
```

## Page Templates:
```python
from reportlab.platypus import PageTemplate, Frame

def create_template():
    frame = Frame(inch, inch, 6.5*inch, 9*inch, id='normal')
    template = PageTemplate(id='standard', frames=frame)
    return template
```

## Memory Optimization for Large Reports:
```python
from reportlab.platypus import SimpleDocTemplate
import io

def generate_streamed_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    # Build document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
```