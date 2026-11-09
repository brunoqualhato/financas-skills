---
name: financas-renda-fixa
description: Compara e simula CDB, LCI, LCA, Tesouro Direto, debêntures, CRI e CRA. Use para avaliar CDI, Selic, IPCA, rendimento líquido, taxa de equivalência, liquidez e FGC.
---

# Renda fixa brasileira

1. Identifique principal, data de aplicação, horizonte, emissor, indexador, taxa contratada, base de contagem, carência, vencimento, liquidez, custos e fluxos. Para ofertas concretas, use o termo do produto. Quando faltarem dados, faça uma simulação com premissas explícitas ou peça os dados decisivos.
2. Use a Taxa DI como referência para ofertas em percentual do CDI. Para uma projeção com CDI anual constante e contrato que aplica o percentual à taxa diária, use fator diário 1 + p × ((1 + c)^(1/252) − 1), com percentual contratado p e CDI anual c em decimais. Eleve aos dias úteis da convenção. Para histórico, multiplique os fatores diários usando as taxas observadas. Respeite arredondamentos e calendário do contrato. [Metodologia da Taxa DI na B3](https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-de-segmentos-e-setoriais/metodologia-do-di.htm)
3. Para prefixados, use a convenção do título. Para IPCA mais taxa real, combine os fatores de inflação e juros conforme o contrato. Separe projeção até o vencimento de venda antecipada, que depende da possibilidade de resgate e do preço de mercado. Use cenários de DI, inflação ou juros quando alterarem a comparação.
4. Verifique IR, IOF e isenções para o produto, investidor e datas conforme a regra vigente. Explicite as bases de cálculo e a ordem das deduções. Para comparar CDB e LCI/LCA, iguale principal e horizonte, calcule o saldo líquido de cada oferta e, se solicitado, encontre a taxa que iguala os saldos.
5. Avalie crédito e liquidez separadamente. Confirme elegibilidade ao FGC, emissor ou conglomerado, exposição agregada e limites vigentes. Para crédito privado, examine garantias contratuais, senioridade e concentração. [Cobertura oficial do FGC](https://www.fgc.org.br/pt-br/sobre-garantia-fgc)

Entregue valor bruto e líquido, taxas efetivas no mesmo horizonte, primeira data de resgate, vencimento e riscos. Identifique taxas futuras como premissas.
