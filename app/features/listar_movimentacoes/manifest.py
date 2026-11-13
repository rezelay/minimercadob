from app.core.types.features import FeatureManifest, MenuItem
from app.features.listar_movimentacoes.routes import bp

manifest = FeatureManifest(
    id="listar-movimentacoes",
    name="Listar Movimentacoes",
    blueprint=bp,
    menu=MenuItem(label="Listar Movimentacoes", endpoint="listar_movimentacoes.page", order=50),
    slots=[],
)
