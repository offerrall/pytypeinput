from pathlib import Path
import shutil
from pytypeinput import analyze_dataclass
from pytypeinput.html import HTMLRenderer

DEMOS_DIR = Path(__file__).parent / "demos"

if DEMOS_DIR.exists():
    shutil.rmtree(DEMOS_DIR)

DEMOS_DIR.mkdir(exist_ok=True)

_CREATED_FILES = set()


def create_dataclass_demo(dataclass_type, filename: str):
    """Create standalone HTML demo from a dataclass.
    
    Args:
        dataclass_type: Dataclass to analyze and render
        filename: Output HTML filename (e.g., "user_form.html")
    
    Raises:
        ValueError: If filename already exists or was already created.
    """
    if filename in _CREATED_FILES:
        raise ValueError(f"File '{filename}' has already been created! Use a different filename.")
    
    file_path = DEMOS_DIR / filename
    if file_path.exists():
        raise ValueError(f"File '{filename}' already exists in {DEMOS_DIR}!")
    
    params = analyze_dataclass(dataclass_type)
    renderer = HTMLRenderer()

    fields_html = '\n'.join(renderer.render_param(p) for p in params)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dataclass_type.__name__} Form</title>
    {renderer.get_styles()}
    <style>
        body {{
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            background: var(--pytypeinput-input-bg, #fff);
            color: var(--pytypeinput-input-text, #000);
            transition: background-color 0.2s, color 0.2s;
        }}
    </style>
</head>
<body>
    {fields_html}
    {renderer.get_validation_script()}
</body>
</html>"""
    
    file_path.write_text(html, encoding='utf-8')
    _CREATED_FILES.add(filename)
    print(f"✓ {filename}")