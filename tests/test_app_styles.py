import re

from app.styles import CSS


def hidden_selectors(css: str) -> list[str]:
    """Selettori delle regole che nascondono qualcosa con `display: none`."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)  # via i commenti
    hidden = []
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if "display: none" in body:
            hidden += [s.strip() for s in selectors.split(",")]
    return hidden


def test_css_does_not_hide_the_header_that_holds_the_sidebar_expand_button():
    # Il pulsante che riapre la sidebar chiusa sta dentro l'intestazione di Streamlit:
    # nasconderla (anche solo la barra degli strumenti) rende impossibile riaprire il menu.
    hidden = hidden_selectors(CSS)
    assert 'header[data-testid="stHeader"]' not in hidden
    assert '[data-testid="stToolbar"]' not in hidden


def test_css_hides_only_the_deploy_and_menu_actions():
    hidden = hidden_selectors(CSS)
    assert '[data-testid="stToolbarActions"]' in hidden


def test_css_makes_the_expand_button_visible_and_clickable_on_the_dark_background():
    assert "stExpandSidebarButton" in CSS
    rule = re.search(r'\[data-testid="stExpandSidebarButton"\]\s*\{([^}]*)\}', CSS)
    assert rule is not None
    assert "color: #E8EEFC" in rule.group(1)
    assert "pointer-events: auto" in rule.group(1)
