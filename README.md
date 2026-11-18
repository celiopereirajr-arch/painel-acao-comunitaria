# Painel de Ação Comunitária

Painel de acompanhamento de ocorrências comunitárias. Projeto da Global Solution 2026 (desafio CitizenTech), FIAP, Ciência da Computação (Online).

## Autores

- Célio Carlos Pereira Junior, RM 574595
- Stela Silva Santos, RM 574593

## Vídeo de apresentação

Link do vídeo no YouTube (não listado): https://youtu.be/ZupyJiaUFf8

## Os bairros simulados, o problema e o público

Os dados representam três freguesias vizinhas de Lisboa: **Arroios**, **Penha de França** e **Areeiro**. Só os nomes dos bairros são reais. **Todas as ocorrências são inventadas** e não descrevem problemas que existam de verdade. Os locais são genéricos (praça, escola, avenida) e nenhum dado é pessoal.

**Problema:** pedidos de melhoria (iluminação, acessibilidade, limpeza e conservação) ficam espalhados. Sem um registro único, ninguém vê o que é mais frequente, o que está parado e o que já foi resolvido, e o morador não consegue acompanhar o andamento.

**Público beneficiado:** moradores, que consultam o andamento pelo código; associação de bairro, que enxerga pendências e prioridades; e pessoas com mobilidade reduzida, porque acessibilidade é uma categoria própria.

## Como executar

Precisa apenas do Python 3 instalado. Nenhuma biblioteca precisa ser instalada.

**Jeito mais fácil:** baixe o projeto, abra o arquivo `src/sistema.py` em um editor (por exemplo o VS Code) e clique no botão de executar.

No menu, digite o número da opção e aperte Enter:

- **11:** demonstração automática (mostra o sistema funcionando do começo ao fim).
- **12:** roda os 28 testes automáticos.

**Pelo terminal:** Em alguns computadores Windows o comando `python` pode ser `py`.

    python src/sistema.py             abre o menu interativo
    python src/sistema.py --demo      roda a demonstração e encerra
    python src/sistema.py --testes    roda os 28 testes e encerra

Os três comandos abrem o mesmo arquivo, `src/sistema.py`.

O código importa duas bibliotecas padrão do Python, que já vêm instaladas: `os`, que monta o caminho da pasta `data` a partir do lugar onde o `sistema.py` está, e `sys`, que lê as opções `--demo` e `--testes`. (`open`, `strip`, `split`) fazem a leitura dos arquivos. Tudo isso foi sugerido pela IA e está explicado em `docs/uso_ia.md`.

## Arquivos

- `src/sistema.py`: o programa. Dados, regras e apresentação ficam em funções separadas e comentadas.
- `data/dados.csv`: as ocorrências simuladas. Os campos são separados por ponto e vírgula: id, categoria, descricao, bairro, local, abertura, status. Todos são obrigatórios.
- `data/historico.csv`: as mudanças de situação simuladas (id, dia, de, para).
- `docs/relatorio.pdf`: relatório do projeto.
- `docs/link_video.txt`: endereço do vídeo.
- `docs/uso_ia.md`: como a inteligência artificial apoiou o projeto.

Os dados não estão dentro do código: o programa lê os dois arquivos da pasta `data` quando inicia.

## Situações das ocorrências

- **aberta:** registrada, mas ainda não examinada por ninguém.
- **em_analise:** alguém está avaliando ou resolvendo.
- **concluida:** resolvida.

Mudanças permitidas: aberta para em_analise, e em_analise para concluida. Pular etapa ou reabrir uma demanda concluída é recusado.

## Estruturas de dados e por que foram escolhidas

- **Lista:** guarda todas as ocorrências para poder percorrê-las (listar, filtrar, calcular).
- **Dicionário (código para ocorrência):** busca direta pelo código, sem percorrer a lista inteira.
- **Fila:** guarda as ocorrências ainda não examinadas. Quem foi registrado primeiro é examinado primeiro.
- **Pilha:** guarda as últimas atualizações. O evento mais recente é o primeiro a ser consultado.
- **Tupla:** cada evento do histórico (código, dia, de, para), que não deve mudar depois de registrado.
- **Dicionário aninhado:** a hierarquia bairro, categoria, códigos. Responde rápido a perguntas como "o que há de limpeza em Penha de França?".
- **Matriz (lista de listas):** quantidades por categoria (linhas) e por situação (colunas), usada nos indicadores.

Também há uma ordenação por inserção, escrita à mão, para listar da ocorrência mais antiga para a mais nova.

## Regras lógicas principais

**Cadastro e validação.** Um registro só entra se: nenhum dos 7 campos obrigatórios está vazio; a categoria (se preenchida) é uma das quatro; a situação (se preenchida) é uma das três; a data de abertura é um número; e o código não existe ainda. Registros recusados ficam guardados com o motivo (opção 10 do menu).

**Expressão booleana documentada.**

    categoria_invalida = (categoria != "") and (categoria not in CATEGORIAS)

Ela só é verdadeira quando a categoria foi preenchida e não está na lista. Categoria vazia: o primeiro termo é falso, essa regra não dispara e a regra dos campos obrigatórios responde "campo obrigatório ausente: categoria". Categoria "barulho": os dois termos são verdadeiros e a resposta é "categoria desconhecida: barulho".

**Consulta.** Busca por código usa o dicionário. O filtro aceita categoria e situação, e cada uma pode ficar livre: `(categoria vazia or categoria igual) and (situação vazia or situação igual)`.

**Atualização.** A mudança só vale se o destino está entre os permitidos para a situação atual (`not (novo in TRANSICOES[atual])` gera a mensagem "Mudança não permitida"). Cada mudança é registrada no histórico e empilhada na pilha. Se a ocorrência estava na fila, sai dela.

**Pendência antiga.** `not concluída and dias abertos >= 15`.

Quando algo não é encontrado ou os dados são inválidos, o sistema diz o que aconteceu em uma frase, sem encerrar o programa.

## Indicadores

Dados de origem: a matriz categoria por situação, montada com laços sobre a lista.

- **Proporção** = quantidade / total x 100, por categoria e por situação.
- **Pendências** = abertas + em análise.
- **Pendências antigas** = pendências abertas há 15 dias ou mais (o dia atual simulado é o 30).
- **Tempo médio até a conclusão** = média de (dia da conclusão menos dia da abertura) das ocorrências concluídas.

Resultado com os dados iniciais (14 ocorrências):

- Iluminação 4 (28,6%), Acessibilidade 3 (21,4%), Limpeza 4 (28,6%), Conservação 3 (21,4%).
- Abertas 6 (42,9%), em análise 4 (28,6%), concluídas 4 (28,6%).
- Pendências: 10 (71,4%). Antigas: 7.
- Tempo médio até a conclusão: (4 + 6 + 3 + 4) / 4 = 4,25 dias simulados.

**Interpretação:** Iluminação e Limpeza concentram mais demandas. A maior parte das demandas ainda está pendente, e a maioria dessas espera há mais de duas semanas. As demandas concluídas foram resolvidas em poucos dias, mas algumas seguem em análise por muito tempo. Os dados são simulados, então isso mostra o método e não descreve um bairro real.

## Exemplo de cadastro, consulta, alteração de status e saída

Trecho da demonstração automática (opção 11 do menu):

    PASSO 3: consulta, todas as ocorrências ABERTAS de ILUMINAÇÃO
    Cód  Categoria       Bairro              Local                   Situação    Aberta no dia
    009  Iluminação      Areeiro             Quadra Poliesportiva    Aberta      13
    Total: 1

    PASSO 4: cadastro válido
    Cadastrado com o código 017

    PASSO 5: cadastro inválido (descrição vazia, categoria ausente)
    Recusado pela validação:
       - campo obrigatório ausente: categoria
       - campo obrigatório ausente: descricao

    PASSO 6: alterar a ocorrência 017 para Em análise
    Ocorrência 017 mudou de Aberta para Em análise.

No menu interativo, o mesmo caminho é: opção 4 (cadastrar), opção 3 (filtrar), opção 6 (atualizar situação), opção 9 (indicadores) e opção 0 (sair).

## Cuidados com acessibilidade, inclusão e privacidade

- **Privacidade:** dados fictícios, locais genéricos e um aviso no cadastro para não escrever dados pessoais. Nenhum campo pede nome, telefone ou endereço.
- **Acessibilidade:** interface só de texto, sem depender de cor. As escolhas são feitas por número, o que reduz erros de digitação, e cada erro explica o que aconteceu.
- **Inclusão:** acessibilidade urbana é uma categoria própria, para que essas demandas não se percam entre as outras.

## Conclusões, limitações e aprendizados

- Lista, fila, pilha, dicionário e matriz resolvem problemas diferentes e trabalham bem juntas em um sistema pequeno. Escolher cada uma pelo que o sistema precisa fazer deixou o código mais simples.
- Os dados são simulados e poucos, então os indicadores demonstram o método.
- O sistema roda em um terminal, para uma pessoa por vez, e as mudanças feitas durante o uso não são gravadas de volta nos arquivos CSV.
- Como evolução: gravar as alterações nos arquivos e aceitar novos bairros e categorias.
