# fotos-skill
Fotos para el uso del Skill de documentos de MBA3

## Resolución mínima

`comprobar_fotos.py` rechaza las fotos de `portada/` y `temas/` de menos de 2400 px de ancho y las de `beneficios/`
de menos de 800 px, y guarda el ancho y el alto de cada foto en `indice.json` (`ancho`, `alto`). Lo ejecuta la CI de
GitHub en cada push y `publicar.bat` (con `--escribir`) antes de publicar.
