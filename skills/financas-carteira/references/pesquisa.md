# Pesquisa e decisão por ativo

## Entrada e ferramentas

Aceite uma lista em linguagem natural, tabela ou arquivo JSON. Converta a lista para o formato de [exemplo](carteira-exemplo.json), preservando lotes. O usuário também pode editar uma cópia do exemplo. Os valores do exemplo são fictícios. Para a primeira rodada, ticker e bolsa bastam para pesquisar um ativo listado. Se bolsa ou moeda forem inferidas, confirme a identificação em fonte pública e registre a inferência. Quantidade, custo e perfil são opcionais para a pesquisa e necessários apenas para conclusões que dependam deles.

Para renda fixa, use um ID local por título e identifique produto e emissor. Solicite a taxa contratada, indexador, data de aplicação, carência, vencimento e liquidez quando necessários para estimar o saldo ou avaliar saída. O termo fornecido pelo usuário prevalece para as condições contratadas. Omita campos desconhecidos. Não pesquise identificadores privados, número de conta, quantidade, custo ou outros dados pessoais na web.

- Execute `python3 scripts/carteira.py plano ARQUIVO.json` a partir do diretório desta skill para validar e obter uma lista de ativos únicos. Corrija entradas ambíguas com base no material do usuário e preserve todos os lotes na consolidação.
- Execute `python3 scripts/carteira.py macro AAAA-MM-DD` para obter CDI diário e meta Selic com data, unidade e URL do Banco Central. Use a data de corte da pesquisa, que pode diferir da data-base das posições. Em falha parcial, preserve as séries válidas e consulte o SGS pela web para as restantes. Verifique o IPCA no IBGE, as decisões e atas no BCB e o câmbio em fonte adequada à data.
- Use a busca web para preços, documentos, proventos, notícias e eventos. As consultas externas devem conter somente os identificadores públicos necessários.

## Pesquisa individual

Para cada ativo único, confirme a identidade e pesquise os itens abaixo. Use a skill da classe para os cálculos e indicadores específicos. Cubra a lista inteira, inclusive quando um ativo ficar com dados insuficientes.

1. **Preço e negociação.** Para ativos listados, confirme preço, moeda, bolsa, horário e atraso ou pregão do fechamento. Use a bolsa ou fonte de mercado identificada. Para renda fixa, distinga saldo no vencimento, saldo estimado na data e valor de saída verificável. Ofertas atuais de outro lote servem apenas como comparação.
2. **Documentos e fundamentos.** Abra o relatório mais recente disponível até a data de corte e verifique sua competência. Para ações brasileiras, use CVM, B3 e RI. Para FIIs, abra informe mensal, relatório gerencial e comunicados. Para ativos dos EUA, use [EDGAR](https://www.sec.gov/edgar/search/) e o emissor ou gestor. Para outros mercados, consulte a bolsa e o regulador locais. Para renda fixa, verifique contrato, crédito do emissor, garantias e condições de resgate.
3. **Dividendos e renda.** Confirme cada provento relevante no comunicado oficial. Registre valor por unidade, tipo, data-com, data ex e pagamento quando disponíveis. Separe anunciado, pago e estimado, bem como amortizações e eventos extraordinários. Calcule o yield de 12 meses com uma cotação datada. Para estimar receita da carteira, use as quantidades e indique se havia posição na data de direito. Para renda fixa, liste cupons e vencimentos conforme o contrato.
4. **Notícias, política e setor.** Comece pelos últimos 30 dias e amplie para eventos ainda materiais. Procure pelo ticker, nome do emissor e setor. Confirme notícias relevantes em fatos, atos ou comunicados oficiais quando disponíveis. Diferencie data do evento e publicação. Identifique o estágio de medidas políticas ou regulatórias, de proposta a vigência. Para cada evento material, mostre o canal pelo qual afeta o ativo, como margem, volume, crédito, capex, custo de capital ou câmbio. Informe direção, horizonte e grau de incerteza. Trate causalidade como hipótese quando as fontes só mostrarem coincidência temporal.
5. **Valuation e cenário.** Compare preço e métricas com pares compatíveis, histórico ou referência de risco e prazo equivalente. Identifique o que os dados sustentam e o que depende de premissas. Se a conclusão for sensível a uma variável, teste pelo menos um cenário adverso. Se a consulta for histórica, exclua documentos e notícias divulgados depois da data de corte.

## Relatório de decisão

Abra com a data de corte e uma tabela de decisão por ativo, seguida de fichas individuais e uma síntese da carteira. Inclua na tabela ação sugerida, razão principal, confiança e gatilho de revisão. Em cada ficha, cite URLs e datas junto de preços, resultados, comunicados e notícias. Distingua fonte primária, dado secundário e inferência.

- **Comprar ou aumentar** quando a avaliação sustentar margem frente ao cenário adverso, liquidez adequada e espaço na carteira. Explique a faixa de preço ou o gatilho que torna a compra defensável.
- **Manter** quando a tese permanecer válida e os riscos couberem no perfil. Diga o que faria a posição mudar de categoria.
- **Reduzir ou vender** quando a tese tiver se deteriorado, a relação entre risco e retorno tiver piorado ou houver concentração incompatível. Considere liquidez, custos e tributos antes de estimar o efeito da saída.
- **Aguardar dados** quando faltar evidência decisiva, houver conflito material entre fontes ou não for possível confirmar preço, identidade ou termos. Com perfil parcial, apresente decisões condicionais e diga que informação pessoal mudaria a avaliação.

Conclua com concentração, calendário confirmado de proventos e vencimentos, riscos em comum e ações prioritárias. Mostre a parcela não precificada ou não pesquisável. Trate as sugestões como apoio à decisão e mantenha a pesquisa em modo de leitura.
