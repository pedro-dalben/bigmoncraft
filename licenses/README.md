# BigMonCraft - Diretório de Licenças de Mods

Este diretório contém o inventário e a documentação completa da auditoria de licenças do modpack **BigMonCraft: Cobblemon Pack** (Minecraft 1.21.1 / Fabric Loader).

## Estrutura de Arquivos

- **`inventory.csv`**: Inventário completo em formato CSV (34 colunas por JAR).
- **`inventory.json`**: Inventário estruturado em formato JSON.
- **`THIRD_PARTY_NOTICES.md`**: Avisos de direitos autorais de terceiros organizados alfabeticamente.
- **`unresolved.md`**: Lista de pendências, restrições e modelos de solicitação de permissão.
- **`sources.json`**: Registro de fontes oficiais e URLs de licenças.
- **`audit-summary.json`**: Resumo quantitativo em JSON.
- **`mods/<mod-id>/`**: Pasta individual por mod contendo `LICENSE.txt`, `NOTICE.txt` (quando existente), `SOURCE.md` e `METADATA.json`.

## Execução da Auditoria Reproduzível

Para re-executar a auditoria e validar os inventários:

```bash
python3 tools/license_audit.py --mods-dir "./mods" --output "./licenses"
```

Modo estrito (`--strict`):

```bash
python3 tools/license_audit.py --mods-dir "./mods" --output "./licenses" --strict
```
