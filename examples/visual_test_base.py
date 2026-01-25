from typing import Any
from dataclasses import is_dataclass
import inspect

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from pytypeinput import analyze_function, analyze_type, analyze_dataclass, analyze_class_init
from pytypeinput.html import HTMLRenderer


def analyze_auto(target: Any, name: str = "field") -> list:
    if inspect.isclass(target):
        if is_dataclass(target):
            return analyze_dataclass(target)
        
        try:
            if issubclass(target, BaseModel):
                from pytypeinput import analyze_pydantic_model
                return analyze_pydantic_model(target)
        except (ImportError, TypeError):
            pass
        
        return analyze_class_init(target)
    
    if callable(target) and hasattr(target, '__code__'):
        return analyze_function(target)
    
    return [analyze_type(target, name=name)]


def create_visual_test_app(target: Any, title: str, name: str = "field") -> FastAPI:
    app = FastAPI()
    
    @app.get("/", response_class=HTMLResponse)
    def render_form():
        params = analyze_auto(target, name=name)
        renderer = HTMLRenderer()
        fields_html = "\n".join(renderer.render_param(p) for p in params)
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - pytypeinput</title>
            {renderer.get_styles()}
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: #f9f9f9;
                }}
                h1 {{
                    margin-bottom: 2rem;
                    color: #333;
                }}
                .form-container {{
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="form-container">
                {fields_html}
            </div>
            {renderer.get_validation_script()}
        </body>
        </html>
        """
        
        return html
    
    return app


def run_visual_test(target: Any, title: str, port: int = 8000, name: str = "field"):
    import uvicorn
    app = create_visual_test_app(target, title, name=name)
    uvicorn.run(app, host="0.0.0.0", port=port)