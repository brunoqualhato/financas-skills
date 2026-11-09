# Acompanhamento mensal e metas

Antes de montar a projeção ou sugerir a destinação dos aportes, pergunte em uma única mensagem pelos dados ainda desconhecidos:

- Qual é o objetivo, o valor, o prazo e se a meta deve ser nominal ou em poder de compra de hoje? Para metas de renda mensal, pergunte pelo valor de renda e valide premissas antes de traduzir isso em patrimônio-alvo.
- Qual é o aporte mínimo, quanto do saldo atual está reservado para a meta e os proventos serão reinvestidos?
- Quais produtos podem entrar ou precisam ficar fora? Confirme a reserva de emergência, a necessidade de liquidez e a tolerância a quedas quando afetarem a escolha.

Use o que o usuário já informou e confirme se deseja reaproveitar metas antigas quando houver mudança de contexto. A mesma carteira pode ter várias metas, como reserva, compra de imóvel e aposentadoria. Identifique quando os cenários disputam o mesmo saldo ou aporte. Em análise simultânea, reserve verbas separadas ou indique a disputa explicitamente. Enquanto aguarda respostas, concilie as posições e pesquise eventos. Só use metas e aportes hipotéticos quando identificados como exemplos.

## Preparação dos extratos

Aceite tabela, texto e arquivos. Transcreva ou converta cada origem para o [CSV normalizado](movimentos-exemplo.csv). Preserve os originais. Use IDs estáveis para o mesmo movimento em exportações sobrepostas. Forneça os movimentos de cada dia em ordem de execução quando a ordem afetar o custo. A ferramenta elimina repetições idênticas e informa quando um ID tem conteúdo divergente.

- Registre aporte e retirada apenas para dinheiro que cruza o perímetro da carteira. Inclua o caixa dentro do perímetro em ambas as avaliações mensais. Compras, vendas, reinvestimentos, proventos e amortizações são internos.
- Use data de liquidação ou crédito para os registros realizados e mantenha a mesma convenção nos saldos. Use valores em BRL e registre taxa de câmbio e origem dos dados de conversão no material de trabalho. Para compras, inclua custos de aquisição no valor. Para vendas, use o valor líquido. Em compra, o delta da posição é positivo. Em venda, é negativo.
- Para uma conversão, use duas linhas com IDs diferentes, uma para remover cotas do ativo original e outra para somar as novas. Use valor zero. Registre a parcela em dinheiro como amortização. Para custo fiscal após conversão ou amortização, use o comunicado da administradora e o extrato em vez de deduzir o custo pelo preço de mercado.
- Use quantidade de abertura e fechamento para conciliar posições. Informe o custo total de abertura quando conhecido. O custo médio calculado é indicativo, em BRL. O resultado é omitido quando há divergência de quantidade ou evento que exige ajuste documental. Mantenha as notas e informes para fins fiscais.

## Executar e interpretar

Preencha uma cópia da [configuração de exemplo](mensal-exemplo.json). Os dados do exemplo são fictícios. Execute a partir da pasta da skill:

```sh
python3 scripts/mensal.py CONFIG.json EXTRATO.csv COMPLEMENTO.csv
```

- Informe se todos os aportes e retiradas foram incluídos. Quando completos, a variação do patrimônio menos o fluxo externo é o resultado em reais após fluxos. Ele inclui valorização, proventos e custos refletidos nos saldos. Os proventos do extrato aparecem em separado e já estão contidos nesse resultado quando creditados dentro da carteira. Para rentabilidade percentual com datas de fluxo, use a metodologia de retorno da skill.
- Nas metas, use hipóteses de retorno anual nominal líquido de custos e tributos, com aportes no fim do mês. A base real desconta a inflação e supõe que os aportes são reajustados pela inflação. Cada cenário informa saldo no prazo, aporte necessário e quando cruza a meta dentro do horizonte. Confirme cenários e inflação com o usuário ou identifique-os como hipóteses.
- No plano de aporte, use orçamento disponível e grupos mutuamente exclusivos que somem o saldo de fechamento. Registre os produtos elegíveis em cada meta e monte alternativas somente com esses produtos. Use grupos_elegiveis para validar as categorias permitidas no plano de aporte. Use grupos por classe, setor ou produto conforme a decisão. Quando o dinheiro já estiver no caixa do fechamento, use caixa_ja_incluido como verdadeiro e informe o grupo caixa. Se parte vier do caixa atual e parte de aporte novo, atualize o caixa e o saldo pelo aporte novo antes da comparação. Compare os pesos resultantes e registre preços, custos e liquidez antes de converter a simulação em quantidades de compra.
- Para cotação, cadastre observações com ativo, data, tipo (fechamento ou intradiario), moeda, valor e fonte (URL). Para dados intradiários, inclua horario_com_fuso com a mesma representação em fontes comparáveis. Confirme ajustes, pregão e instrumento antes de comparar. O relatório sinaliza valores divergentes para a mesma referência e preserva cada observação. A coleta é feita pelo agente com acesso à web.
- Para eventos, informe data, ativo, tipo, status, fonte (URL) e providencia quando houver. Marque separadamente anunciado, confirmado e creditado conforme a evidência disponível. Pesquise a fonte primária e atualize prazos ao receber comunicados novos. O calendário lista os eventos do mês em diante.

Entregue resumo do patrimônio, fluxo externo, resultado em reais quando apurável, proventos creditados, divergências, trajetória por meta, alternativas para o próximo aporte e eventos que exigem ação. Apresente a data de corte e as lacunas que afetam a decisão.
