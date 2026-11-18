# Uso de inteligência artificial

Ferramenta usada: Claude (Anthropic).

## Onde a IA apoiou

- Discussão da ideia do projeto e do formato dos dados simulados.
- Apoio na criação dos testes automáticos.
- Criação dos dados fictícios de `data/dados.csv` e `data/historico.csv`.

## Recursos de Python sugeridos pela IA

O enunciado permite "leitura simples de arquivos se necessário". Os recursos abaixo foram sugeridos pela IA, que explicou suas finalidades e como utilizá-los.

- `os`: usada com `os.path` para montar o caminho da pasta `data` a partir do lugar onde o `sistema.py` está guardado. Assim o programa acha os arquivos mesmo quando é executado de outra pasta.
- `sys`: usada para ler as opções `--demo` e `--testes` digitadas na linha de comando (`sys.argv`) e para encerrar o programa com um código de saída nos testes (`sys.exit`).
- `open()`: abre o arquivo para leitura; `.close()` fecha depois de ler.
- `.strip()`: tira espaços e a quebra de linha do começo e do fim de um texto.
- `.split(";")`: corta uma linha do arquivo em pedaços, separando nos pontos e vírgulas.

## Como os resultados foram verificados

- O sistema tem 28 testes automáticos (opção 12 do menu ou `--testes`). Todos passaram.
- A demonstração automática (opção 11 do menu ou `--demo`) foi executada e as saídas foram conferidas contra os números do relatório.
- Os valores dos indicadores foram recalculados à mão (proporções, pendências e tempo médio) e batem com a saída do programa.
