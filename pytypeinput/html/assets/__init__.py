import importlib.resources

def _load_asset(filename: str) -> str:
    return importlib.resources.files(__package__).joinpath(filename).read_text(encoding='utf-8')

DEFAULT_STYLES = _load_asset('styles.css')
DEFAULT_VALIDATION_SCRIPT = f"<script>{_load_asset('validation.js')}</script>"