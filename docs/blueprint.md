# **App Name**: Privacy Pal

## Core Features:

- File Upload and Type Detection: Allows users to upload .txt, .csv, .log, .md, .json, and .pdf files and automatically detects the file type. Whit Drag and Drop
- Text Redaction: Detects and redacts sensitive data in text files by replacing it with tokens or masking it while preserving length and format.
- PDF Redaction: Detects and redacts sensitive data in PDF files by drawing black rectangles over the matched content within the PDF.
- Rule Management: Enables users to activate or deactivate individual redaction rules for different types of data.
- Strategy Selection (Text): Offers users the option to select different redaction strategies for text files, such as token replacement or masking.
- Original and Redacted View: Displays both the original and redacted content side-by-side. For PDFs, it provides an indicator and a download button for the redacted PDF.
- Credit Card Validation: Applies Luhn algorithm to credit card numbers before redaction.

## Style Guidelines:

- Primary color: HSL(210, 70%, 50%) - RGB(#3399FF). A vibrant blue to represent security and trust.
- Background color: HSL(210, 20%, 95%) - RGB(#F0F8FF). A very light blue to ensure comfortable readability.
- Accent color: HSL(180, 60%, 40%) - RGB(#33BDBD). A contrasting teal to highlight important actions and elements.
- Font pairing: 'Inter' (sans-serif) for both headlines and body text. This font is chosen for its modern, neutral look and readability.
- Code font: 'Source Code Pro' for displaying code snippets within the app.
- Use simple and clear icons to represent file types, actions, and settings.
- Implement a clear, intuitive, and responsive layout, optimizing readability and user experience across different screen sizes.