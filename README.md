# Skills de finanças

Para analisar seus investimentos, envie ao agente uma lista como esta, substituindo os exemplos pelas suas posições.

> Analise minha carteira ativo por ativo. Tenho 20 PETR4, 5 HGLG11, 2,5 VOO e um CDB do Banco X a 110% do CDI com vencimento em outubro de 2027. Meu objetivo é renda e crescimento em cinco anos. Verifique cotações, fundamentos, proventos, notícias e riscos políticos e setoriais. Diga em quais condições faz sentido comprar, manter, reduzir ou vender cada ativo e cite as fontes.

Você também pode copiar e preencher o [modelo JSON](skills/financas-carteira/references/carteira-exemplo.json). Use a data à qual as posições se referem. Para ativos listados, informe ticker, bolsa e moeda. Quantidade e custo ajudam no cálculo da alocação, renda e efeitos de saída. Para renda fixa, informe produto, emissor, identificador local, indexador, taxa, aplicação, vencimento e liquidez, quando disponíveis.

A entrada principal é a [skill de carteira](skills/financas-carteira/SKILL.md). Ela orienta o agente a pesquisar cada ativo pela web e usar as skills de [ações](skills/financas-acoes-br/SKILL.md), [FIIs](skills/financas-fiis/SKILL.md), [mercado internacional](skills/financas-internacional/SKILL.md) e [renda fixa](skills/financas-renda-fixa/SKILL.md).

## Ferramenta de terminal

Na raiz do projeto, com Python 3.8 ou superior, execute os comandos abaixo. Troque a data do segundo comando pelo corte da pesquisa.

```sh
python3 skills/financas-carteira/scripts/carteira.py plano skills/financas-carteira/references/carteira-exemplo.json
python3 skills/financas-carteira/scripts/carteira.py macro 2026-11-09
```

O primeiro comando valida o cadastro e agrupa posições locais para pesquisa. O segundo consulta CDI e meta Selic diretamente no Banco Central e precisa de acesso à internet. Cotações, proventos, notícias e documentos são pesquisados pelo agente com acesso à web.

## Acompanhamento mensal

Peça um relatório mensal ou um plano para uma meta. O agente pergunta pelo objetivo, valor, prazo, aporte, produtos permitidos e necessidade de liquidez. Pode trabalhar com mais de uma meta e com dados fornecidos no chat ou em arquivos locais.

Consulte o [fluxo mensal](skills/financas-carteira/references/fluxo-mensal.md) e teste com os exemplos fictícios.

```sh
python3 skills/financas-carteira/scripts/mensal.py \
  skills/financas-carteira/references/mensal-exemplo.json \
  skills/financas-carteira/references/movimentos-exemplo.csv
```
