# Como colaborar no GravityPort

O GravityPort é um fork comunitário baseado em [LucaPazienza/gravityrush_pc](https://github.com/LucaPazienza/gravityrush_pc), sob GPL-2.0-or-later. A prioridade atual é a estabilidade de **Gravity Rush Remastered CUSA01113 v01.00** no Windows.

## Issues de bugs

Informe versão do GravityPort, versão do Windows, GPU e driver, modo de upscale, resolução e limite de FPS. Explique o que esperava, o que ocorreu e como reproduzir. Para bugs visuais, informe FSR3/FSR4/DLSS e se a cena já tinha aquecido o cache de shaders.

**Nunca anexe** arquivos `eboot.bin`, `.pkg`, `.psarc`, `.prx`, saves pessoais, chaves, tokens, screenshots com dados pessoais ou outros conteúdos comerciais. Antes de anexar logs, remova caminhos de perfil, nomes e informações privadas.

## Pull requests

- Indique o comportamento anterior e o novo, e confirme as plataformas testadas. Não apresente logs de FPS como prova de frame generation ou sincronização física.
- Limite as mudanças ao necessário e preserve autoria, histórico e licenças. Não altere dependências de submódulos sem vincular sua origem e commit públicos.
- Novos modelos/bibliotecas de terceiros precisam de procedência, condições de distribuição, licença e teste isolado.
- Adicione testes que protejam o fluxo, sobretudo para vídeos, controls, gamepad, FSR4 e empacotamento.
- Rode `python -m unittest discover -s tests -p "test_*.py"` e o smoke test Windows quando houver alterações no runtime ou launcher.
- Recursos experimentais devem ser desativados por padrão até serem testados no jogo e não podem ser descritos como completos antes disso.

## Licenças e publicação

Código próprio/derivado GPL-2.0-or-later, respeitando licenças específicas de componentes. Não redistribua SDKs ou DLLs NVIDIA proprietários por este repositório; alterações de código devem manter a separação de SDKs licenciados. Modelos de FSR4 devem preservar seus avisos e origens.

Referências: [créditos e colaboradores](docs/GRAVITYPORT-CREDITS.md), [estado técnico](GRAVITYPORT.md), [instalador Windows](docs/INSTALLER.md) e [política de release](docs/PUBLIC-RELEASE.md).
