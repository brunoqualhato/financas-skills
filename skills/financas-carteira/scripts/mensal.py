#!/usr/bin/env python3
"""Relatório mensal com extratos locais, metas e simulações de aporte."""
import argparse
import csv
import json
from calendar import monthrange
from decimal import ROUND_CEILING, Decimal, DecimalException
from pathlib import Path

from carteira import data_iso

ZERO = Decimal(0)
CEM = Decimal(100)
CENTAVO = Decimal("0.01")
MOVIMENTOS = {"aporte", "retirada", "compra", "venda", "provento", "amortizacao", "conversao"}


def decimal(valor, campo, minimo=None):
    if isinstance(valor, bool) or valor is None:
        raise ValueError(f"{campo} deve ser numérico")
    try:
        valor = Decimal(str(valor))
    except DecimalException:
        raise ValueError(f"{campo} deve ser numérico e usar ponto decimal") from None
    if not valor.is_finite() or (minimo is not None and valor < minimo):
        raise ValueError(f"{campo} fora do intervalo permitido")
    return valor


def moeda(valor):
    return str(valor.quantize(CENTAVO))


def calcular_xirr(fluxos, palpite=0.1, max_iter=100, tol=1e-7):
    if not fluxos or len(fluxos) < 2:
        return None
    fluxos_validos = [(d, float(v)) for d, v in fluxos if v != 0]
    has_pos = any(v > 0 for _, v in fluxos_validos)
    has_neg = any(v < 0 for _, v in fluxos_validos)
    if not (has_pos and has_neg):
        return None
    d0 = min(d for d, _ in fluxos_validos)
    r = palpite
    for _ in range(max_iter):
        f = 0.0
        df = 0.0
        for d, v in fluxos_validos:
            dt = (d - d0).days / 365.0
            denom = (1.0 + r) ** dt
            if denom == 0:
                return None
            f += v / denom
            if dt != 0:
                df -= dt * v / ((1.0 + r) ** (dt + 1.0))
        if abs(df) < 1e-12:
            break
        r_novo = r - f / df
        if abs(r_novo - r) < tol:
            return r_novo
        r = r_novo
        if r <= -0.9999:
            r = -0.9999
    return r


def simular_meta(meta, saldo):
    alvo = decimal(meta["valor_brl"], "valor da meta", CENTAVO)
    aporte = decimal(meta["aporte_mensal_brl"], "aporte mensal", ZERO)
    meses = meta["prazo_meses"]
    if type(meses) is not int or not 1 <= meses <= 1200:
        raise ValueError("prazo_meses deve ser um inteiro entre 1 e 1200")
    base = meta["base"]
    if base not in {"nominal", "real"}:
        raise ValueError("base deve ser nominal ou real")
    if not meta["retornos_liquidos_aa_pct"]:
        raise ValueError("informe pelo menos um cenário de retorno")
    inflacao = decimal(meta["inflacao_aa_pct"], "inflação", ZERO) / CEM if base == "real" else ZERO
    cenarios = []
    for premissa in meta["retornos_liquidos_aa_pct"]:
        anual = decimal(premissa, "retorno anual líquido") / CEM
        if anual <= -1:
            raise ValueError("retorno anual deve ser maior que -100%")
        fator = ((1 + anual) / (1 + inflacao)) ** (Decimal(1) / 12)
        saldo_mes = saldo
        fator_aportes = ZERO
        mes_meta = 0 if saldo >= alvo else None
        for mes in range(1, meses + 1):
            saldo_mes = saldo_mes * fator + aporte
            fator_aportes = fator_aportes * fator + 1
            if mes_meta is None and saldo_mes >= alvo:
                mes_meta = mes
        necessario = max(ZERO, (alvo - saldo * fator ** meses) / fator_aportes)
        cenarios.append({
            "retorno_nominal_liquido_aa_pct": str(anual * CEM),
            "saldo_no_prazo_brl": moeda(saldo_mes),
            "faltante_no_prazo_brl": moeda(max(ZERO, alvo - saldo_mes)),
            "mes_em_que_atinge_meta_no_prazo": mes_meta,
            "aporte_mensal_necessario_brl": str(necessario.quantize(CENTAVO, rounding=ROUND_CEILING)),
        })
    return {
        "objetivo": meta["objetivo"],
        "base": base,
        "valor_brl": moeda(alvo),
        "saldo_inicial_brl": moeda(saldo),
        "aporte_mensal_brl": moeda(aporte),
        "prazo_meses": meses,
        "inflacao_aa_pct": str(inflacao * CEM) if base == "real" else None,
        "produtos_elegiveis": meta.get("produtos_elegiveis"),
        "aportes_reajustados_pela_inflacao": base == "real",
        "cenarios": cenarios,
    }


def ler_movimentos(arquivos):
    movimentos = {}
    for arquivo in arquivos:
        with arquivo.open(encoding="utf-8-sig", newline="") as entrada:
            leitor = csv.DictReader(entrada)
            esperados = {"id", "data", "tipo", "ativo", "quantidade_delta", "valor_brl"}
            if not esperados.issubset(leitor.fieldnames or []):
                raise ValueError(f"{arquivo}: cabeçalho incompleto")
            for linha in leitor:
                try:
                    id_mov = linha["id"].strip()
                    tipo = linha["tipo"].strip()
                    ativo = linha["ativo"].strip().upper()
                    if not id_mov or tipo not in MOVIMENTOS:
                        raise ValueError("ID ou tipo inválido")
                    externo = tipo in {"aporte", "retirada"}
                    if externo == bool(ativo):
                        raise ValueError("informe ativo apenas nas movimentações internas")
                    quantidade = decimal(linha["quantidade_delta"] or "0", "quantidade_delta")
                    valor = decimal(linha["valor_brl"] or "0", "valor_brl", ZERO)
                    if (tipo == "compra" and quantidade <= 0) or (tipo == "venda" and quantidade >= 0):
                        raise ValueError("compra deve somar cotas e venda deve subtrair cotas")
                    if tipo in {"compra", "venda"} and not valor:
                        raise ValueError("compra ou venda exige valor positivo")
                    if tipo == "conversao" and (not quantidade or valor):
                        raise ValueError("conversão exige delta não nulo e valor zero; registre o dinheiro em amortização")
                    if tipo not in {"compra", "venda", "conversao"} and (quantidade or not valor):
                        raise ValueError("movimento financeiro exige valor positivo e quantidade vazia")
                    mov = (data_iso(linha["data"]), tipo, ativo, quantidade, valor)
                    if id_mov in movimentos and movimentos[id_mov] != mov:
                        raise ValueError(f"ID duplicado com conteúdo divergente: {id_mov}")
                    movimentos[id_mov] = mov
                except (ValueError, AttributeError) as erro:
                    raise ValueError(f"{arquivo}, linha {leitor.line_num}: {erro}") from None
    return sorted(movimentos.values(), key=lambda movimento: movimento[0])


def pesos(saldos):
    total = sum(saldos.values(), ZERO)
    return {grupo: moeda(valor * CEM / total) if total else None for grupo, valor in saldos.items()}


def comparar_aportes(saldos, plano):
    orcamento = decimal(plano["disponivel_brl"], "orçamento do aporte", ZERO)
    atuais = dict(saldos)
    elegiveis = set(plano["grupos_elegiveis"]) if "grupos_elegiveis" in plano else None
    alternativas = []
    for nome, alocacoes in plano["alternativas"].items():
        valores = {grupo: decimal(valor, grupo, ZERO) for grupo, valor in alocacoes.items()}
        if "caixa" in valores or (elegiveis is not None and valores.keys() - elegiveis):
            raise ValueError(f"{nome}: alocação contém grupo não elegível")
        total = sum(valores.values(), ZERO)
        if total > orcamento:
            raise ValueError(f"{nome}: compras excedem orçamento")
        posteriores = dict(atuais)
        for grupo, valor in valores.items():
            posteriores[grupo] = posteriores.get(grupo, ZERO) + valor
        if plano.get("caixa_ja_incluido", False):
            caixa = posteriores.get("caixa", ZERO) - total
            if caixa < 0:
                raise ValueError(f"{nome}: compras excedem caixa do fechamento")
            posteriores["caixa"] = caixa
        else:
            posteriores["caixa"] = posteriores.get("caixa", ZERO) + orcamento - total
        alternativas.append({
            "cenario": nome, "compras_brl": {k: moeda(v) for k, v in valores.items()},
            "saldo_do_orcamento_brl": moeda(orcamento - total),
            "pesos_pct": pesos(posteriores),
        })
    return alternativas


def conciliar(posicoes, movimentos):
    resultado = {}
    for ativo, posicao in posicoes.items():
        ativo = ativo.upper()
        quantidade = decimal(posicao["abertura"], "quantidade de abertura", ZERO)
        custo = posicao.get("custo_total_abertura_brl")
        custo = decimal(custo, "custo de abertura", ZERO) if custo is not None else (None if quantidade else ZERO)
        if not quantidade and custo:
            raise ValueError(f"{ativo}: custo sem posição de abertura")
        for _, tipo, codigo, delta, valor in movimentos:
            if codigo != ativo:
                continue
            nova = quantidade + delta
            if nova < 0:
                custo = None
            elif not nova:
                custo = ZERO
            elif tipo in {"conversao", "amortizacao"}:
                custo = None
            elif custo is not None and tipo == "compra":
                custo += valor
            elif custo is not None and tipo == "venda" and quantidade > 0:
                custo *= nova / quantidade
            quantidade = nova
        observado = decimal(posicao["fechamento"], "quantidade de fechamento", ZERO)
        resultado[ativo] = {
            "esperado": str(quantidade),
            "observado": str(observado),
            "diferenca": str(observado - quantidade),
            "custo_total_brl": moeda(custo) if custo is not None and observado == quantidade else None,
            "custo_medio_brl": str((custo / quantidade).quantize(Decimal("0.000001")))
            if custo is not None and observado == quantidade and quantidade > 0 else None,
        }
    return resultado


def verificar_cotacoes(cotacoes):
    grupos = {}
    for cotacao in cotacoes:
        ativo = cotacao["ativo"].upper()
        data = str(data_iso(cotacao["data"]))
        tipo = cotacao["tipo"]
        if tipo not in {"fechamento", "intradiario"}:
            raise ValueError("tipo de cotação inválido")
        horario = cotacao.get("horario_com_fuso") if tipo == "intradiario" else None
        if tipo == "intradiario" and not horario:
            raise ValueError("cotação intradiária exige horário e fuso")
        fonte = cotacao["fonte"]
        if not fonte.startswith(("https://", "http://")):
            raise ValueError("cotação precisa de URL da fonte")
        valor = decimal(cotacao["valor"], "cotação", Decimal("0.000001"))
        chave = (ativo, data, tipo, cotacao["moeda"].upper(), horario)
        grupos.setdefault(chave, []).append({"fonte": fonte, "valor": str(valor)})
    return [
        {"ativo": ativo, "data": data, "tipo": tipo, "moeda": divisa, "horario_com_fuso": horario,
         "divergencia": len({Decimal(c["valor"]) for c in dados}) > 1, "observacoes": dados}
        for (ativo, data, tipo, divisa, horario), dados in grupos.items()
    ]


def relatorio(config, arquivos):
    inicio = data_iso(config["mes"] + "-01")
    fim = inicio.replace(day=monthrange(inicio.year, inicio.month)[1])
    inicial = decimal(config["saldo_abertura_brl"], "saldo inicial", ZERO)
    final = decimal(config["saldo_fechamento_brl"], "saldo final", ZERO)
    saldos = {k: decimal(v, k, ZERO) for k, v in config.get("saldos_por_grupo_brl", {}).items()}
    if saldos and sum(saldos.values(), ZERO) != final:
        raise ValueError("grupos devem somar o saldo de fechamento")
    totais = dict.fromkeys(MOVIMENTOS, ZERO)
    movimentos = [mov for mov in ler_movimentos(arquivos) if inicio <= mov[0] <= fim]
    for _, tipo, _, _, valor in movimentos:
        totais[tipo] += valor
    conciliacao = conciliar(config.get("posicoes_conciliar", {}), movimentos)
    eventos = []
    for evento in config.get("eventos", []):
        dia = data_iso(evento["data"])
        if not evento["fonte"].startswith(("https://", "http://")):
            raise ValueError("evento precisa de URL da fonte")
        if dia >= inicio:
            eventos.append(evento)
    fluxo = totais["aporte"] - totais["retirada"]
    if config.get("fluxos_externos_completos") is True and not arquivos:
        raise ValueError("forneça um CSV, ainda que só com cabeçalho, para confirmar o fluxo completo")
    xirr_anualizado = None
    if config.get("fluxos_externos_completos") is True:
        fluxos = []
        if inicial > ZERO:
            fluxos.append((inicio, -float(inicial)))
        for dia, tipo, _, _, valor in movimentos:
            if tipo == "aporte" and valor > ZERO:
                fluxos.append((dia, -float(valor)))
            elif tipo == "retirada" and valor > ZERO:
                fluxos.append((dia, float(valor)))
        if final > ZERO:
            fluxos.append((fim, float(final)))
        taxa = calcular_xirr(fluxos)
        if taxa is not None:
            xirr_anualizado = str((Decimal(str(taxa)) * CEM).quantize(CENTAVO))
    resultado = {
        "mes": config["mes"],
        "saldo_abertura_brl": moeda(inicial),
        "saldo_fechamento_brl": moeda(final),
        "movimentos_brl": {k: moeda(v) for k, v in sorted(totais.items())},
        "variacao_patrimonial_brl": moeda(final - inicial),
        "fluxo_externo_liquido_brl": moeda(fluxo),
        "resultado_apos_fluxos_brl": moeda(final - inicial - fluxo) if config.get("fluxos_externos_completos") is True else None,
        "xirr_anualizado_pct": xirr_anualizado,
        "conciliacao_quantidades": conciliacao,
        "pesos_fechamento_pct": pesos(saldos),
        "cotacoes_conferidas": verificar_cotacoes(config.get("cotacoes", [])),
        "eventos": sorted(eventos, key=lambda evento: evento["data"]),
        "metas": [],
    }
    for meta in config.get("metas", []):
        saldo_meta = decimal(meta["saldo_destinado_brl"], "saldo destinado", ZERO)
        if saldo_meta > final:
            raise ValueError("saldo destinado à meta excede o patrimônio")
        resultado["metas"].append(simular_meta(meta, saldo_meta))
    if "plano_aporte" in config:
        if not saldos:
            raise ValueError("informe saldos por grupo para comparar aportes")
        resultado["alternativas_aporte"] = comparar_aportes(saldos, config["plano_aporte"])
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("configuracao", type=Path)
    parser.add_argument("extratos", nargs="*", type=Path, help="CSVs locais já normalizados")
    args = parser.parse_args()
    try:
        config = json.loads(args.configuracao.read_text(encoding="utf-8"), parse_float=Decimal)
        print(json.dumps(relatorio(config, args.extratos), ensure_ascii=False, indent=2, default=str))
    except (OSError, ValueError, KeyError, TypeError, DecimalException, csv.Error) as erro:
        parser.exit(2, f"Erro: {erro}\n")


if __name__ == "__main__":
    main()
