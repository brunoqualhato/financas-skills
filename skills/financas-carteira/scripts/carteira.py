#!/usr/bin/env python3
"""Valida a carteira local, agrupa posições para pesquisa e consulta o SGS."""
import argparse
import json
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

LISTADOS = {"acao_br", "fii", "internacional"}
CLASSES = LISTADOS | {"renda_fixa"}
SERIES = {
    "cdi": (12, "% ao dia"),
    "meta_selic": (432, "% ao ano"),
    "dolar_ptax": (1, "BRL por USD"),
}
CAMPOS_POSICAO = {
    "classe", "ticker", "bolsa", "moeda", "quantidade", "preco_medio",
    "id_titulo", "produto", "emissor", "indexador", "taxa_contratada",
    "valor_aplicado", "data_aplicacao", "vencimento", "liquidez",
}


def texto(posicao, campo):
    valor = posicao.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} deve ser texto preenchido")
    return valor.strip()


def data_iso(valor):
    if not isinstance(valor, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
        raise ValueError("use datas no formato AAAA-MM-DD")
    return date.fromisoformat(valor)


def numero(posicao, campo):
    valor = posicao[campo]
    if isinstance(valor, bool) or not isinstance(valor, (str, int, Decimal)):
        raise ValueError(f"{campo} deve ser um número positivo")
    try:
        convertido = Decimal(valor)
    except InvalidOperation:
        raise ValueError(f"{campo} deve ser um número com ponto decimal") from None
    if not convertido.is_finite() or convertido <= 0:
        raise ValueError(f"{campo} deve ser um número positivo")


def plano(carteira):
    if not isinstance(carteira, dict):
        raise ValueError("a carteira deve ser um objeto JSON")
    data_base = data_iso(carteira.get("data_base"))
    perfil = carteira.get("perfil", {})
    if not isinstance(perfil, dict):
        raise ValueError("perfil deve ser um objeto")
    posicoes = carteira.get("posicoes")
    if not isinstance(posicoes, list) or not posicoes:
        raise ValueError("informe pelo menos uma posição")
    grupos = {}
    for indice, posicao in enumerate(posicoes, 1):
        try:
            if not isinstance(posicao, dict):
                raise ValueError("deve ser um objeto")
            extras = posicao.keys() - CAMPOS_POSICAO
            if extras:
                raise ValueError(f"campos desconhecidos: {', '.join(sorted(extras))}")
            classe = texto(posicao, "classe")
            if classe not in CLASSES:
                raise ValueError(f"classe desconhecida: {classe}")
            moeda = texto(posicao, "moeda").upper()
            if not re.fullmatch(r"[A-Z]{3}", moeda):
                raise ValueError("moeda deve ser um código de três letras")
            if classe in LISTADOS:
                ticker = texto(posicao, "ticker").upper()
                bolsa = texto(posicao, "bolsa").upper()
                identidade = (bolsa, ticker)
                pesquisa = {"ticker": ticker, "bolsa": bolsa}
            else:
                produto = texto(posicao, "produto")
                emissor = texto(posicao, "emissor")
                id_titulo = texto(posicao, "id_titulo")
                identidade = ("renda_fixa", emissor.casefold(), id_titulo.casefold())
                pesquisa = {"produto": produto, "emissor": emissor, "id_titulo": id_titulo}
            for campo in ("quantidade", "preco_medio", "valor_aplicado"):
                if posicao.get(campo) is not None:
                    numero(posicao, campo)
            aplicacao = posicao.get("data_aplicacao")
            vencimento = posicao.get("vencimento")
            if aplicacao is not None and data_iso(aplicacao) > data_base:
                raise ValueError("data_aplicacao posterior à data-base")
            if vencimento is not None:
                vencimento = data_iso(vencimento)
                if aplicacao is not None and vencimento < data_iso(aplicacao):
                    raise ValueError("vencimento anterior à aplicação")
            pesquisa.update(classe=classe, moeda=moeda)
            grupo = grupos.setdefault(identidade, {"pesquisa": pesquisa, "posicoes": []})
            if grupo["pesquisa"] != pesquisa:
                raise ValueError("posições do mesmo ativo têm classe, moeda ou identificação divergentes")
            if classe == "renda_fixa" and grupo["posicoes"]:
                anterior = grupo["posicoes"][0]
                for campo in ("indexador", "taxa_contratada", "vencimento", "liquidez"):
                    if anterior.get(campo) != posicao.get(campo):
                        raise ValueError("use IDs distintos para títulos com condições diferentes")
            grupo["posicoes"].append(posicao)
        except ValueError as erro:
            raise ValueError(f"posição {indice}: {erro}") from None
    return {"data_base": str(data_base), "perfil": perfil, "ativos": list(grupos.values())}


def macro(data_base):
    inicio = data_base - timedelta(days=14)
    consulta = urlencode({
        "formato": "json", "dataInicial": inicio.strftime("%d/%m/%Y"),
        "dataFinal": data_base.strftime("%d/%m/%Y"),
    })
    resultado = {}
    for nome, (codigo, unidade) in SERIES.items():
        fonte = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?{consulta}"
        item = {"fonte": fonte, "unidade": unidade}
        try:
            with urlopen(fonte, timeout=10) as resposta:
                dados = json.load(resposta)
            if not isinstance(dados, list):
                raise ValueError("resposta fora do formato esperado")
            observacoes = []
            for registro in dados:
                dia = datetime.strptime(registro["data"], "%d/%m/%Y").date()
                valor = Decimal(registro["valor"])
                if inicio <= dia <= data_base and valor.is_finite():
                    observacoes.append((dia, valor))
            if not observacoes:
                raise ValueError("nenhuma observação no intervalo")
            dia, valor = max(observacoes, key=lambda observacao: observacao[0])
            item.update(data=str(dia), valor=str(valor))
        except (OSError, URLError, ValueError, TypeError, KeyError, InvalidOperation) as erro:
            item["erro"] = str(erro)
        resultado[nome] = item
    return resultado


def aliquota_ir(dias):
    if not isinstance(dias, int) or dias < 0:
        raise ValueError("dias deve ser um número inteiro não negativo")
    if dias <= 180:
        return {"dias_corridos": dias, "aliquota_pct": "22.5", "faixa": "até 180 dias"}
    elif dias <= 360:
        return {"dias_corridos": dias, "aliquota_pct": "20.0", "faixa": "181 a 360 dias"}
    elif dias <= 720:
        return {"dias_corridos": dias, "aliquota_pct": "17.5", "faixa": "361 a 720 dias"}
    return {"dias_corridos": dias, "aliquota_pct": "15.0", "faixa": "acima de 720 dias"}


def calcular_ir_comando(termo1, termo2=None):
    if termo2 is not None:
        inicio = data_iso(termo1)
        fim = data_iso(termo2)
        if fim < inicio:
            raise ValueError("data final anterior à data inicial")
        dias = (fim - inicio).days
    else:
        try:
            dias = int(termo1)
        except ValueError:
            raise ValueError("informe a quantidade de dias ou duas datas no formato AAAA-MM-DD") from None
    res = aliquota_ir(dias)
    if termo2 is not None:
        res["data_inicio"] = str(data_iso(termo1))
        res["data_fim"] = str(data_iso(termo2))
    return res


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)
    comandos.add_parser("plano", help="valida e lista os ativos únicos").add_argument(
        "arquivo", type=Path
    )
    comandos.add_parser("macro", help="consulta CDI, meta Selic e PTAX").add_argument(
        "data_base", type=data_iso
    )
    parser_ir = comandos.add_parser("ir", help="calcula alíquota regressiva de IR para renda fixa")
    parser_ir.add_argument("termo1", help="dias corridos ou data inicial (AAAA-MM-DD)")
    parser_ir.add_argument("termo2", nargs="?", default=None, help="data final opcional (AAAA-MM-DD)")
    args = parser.parse_args()
    try:
        if args.comando == "plano":
            dados = plano(json.loads(args.arquivo.read_text(encoding="utf-8"), parse_float=Decimal))
        elif args.comando == "macro":
            dados = macro(args.data_base)
        else:
            dados = calcular_ir_comando(args.termo1, args.termo2)
    except (OSError, ValueError) as erro:
        parser.exit(2, f"Erro: {erro}\n")
    print(json.dumps(dados, ensure_ascii=False, indent=2, default=str, allow_nan=False))
    return int(args.comando == "macro" and any("erro" in item for item in dados.values()))


if __name__ == "__main__":
    raise SystemExit(main())
