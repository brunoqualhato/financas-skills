import unittest
from decimal import Decimal
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "financas-carteira" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from carteira import plano, aliquota_ir, calcular_ir_comando


class TestCarteira(unittest.TestCase):
    def setUp(self):
        self.carteira_valida = {
            "data_base": "2026-11-09",
            "perfil": {
                "objetivo": "renda",
                "horizonte": "5 anos"
            },
            "posicoes": [
                {
                    "classe": "acao_br",
                    "ticker": "PETR4",
                    "bolsa": "B3",
                    "moeda": "BRL",
                    "quantidade": 100,
                    "preco_medio": "35.50"
                },
                {
                    "classe": "renda_fixa",
                    "id_titulo": "CDB-01",
                    "produto": "CDB",
                    "emissor": "Banco ABC",
                    "moeda": "BRL",
                    "indexador": "CDI",
                    "taxa_contratada": "110% do CDI",
                    "valor_aplicado": "5000.00",
                    "data_aplicacao": "2026-01-01",
                    "vencimento": "2027-01-01",
                    "liquidez": "no vencimento"
                }
            ]
        }

    def test_plano_valido(self):
        resultado = plano(self.carteira_valida)
        self.assertEqual(resultado["data_base"], "2026-11-09")
        self.assertEqual(len(resultado["ativos"]), 2)
        ativo_acao = resultado["ativos"][0]["pesquisa"]
        self.assertEqual(ativo_acao["ticker"], "PETR4")
        self.assertEqual(ativo_acao["classe"], "acao_br")

    def test_plano_campos_desconhecidos(self):
        invalida = dict(self.carteira_valida)
        invalida["posicoes"] = [
            {"classe": "acao_br", "ticker": "VALE3", "bolsa": "B3", "moeda": "BRL", "campo_extra": "erro"}
        ]
        with self.assertRaises(ValueError) as ctx:
            plano(invalida)
        self.assertIn("campos desconhecidos", str(ctx.exception))

    def test_plano_classe_invalida(self):
        invalida = dict(self.carteira_valida)
        invalida["posicoes"] = [
            {"classe": "cripto_nao_suportada", "ticker": "BTC", "bolsa": "B3", "moeda": "BRL"}
        ]
        with self.assertRaises(ValueError) as ctx:
            plano(invalida)
        self.assertIn("classe desconhecida", str(ctx.exception))

    def test_aliquota_ir(self):
        self.assertEqual(aliquota_ir(0)["aliquota_pct"], "22.5")
        self.assertEqual(aliquota_ir(180)["aliquota_pct"], "22.5")
        self.assertEqual(aliquota_ir(181)["aliquota_pct"], "20.0")
        self.assertEqual(aliquota_ir(360)["aliquota_pct"], "20.0")
        self.assertEqual(aliquota_ir(361)["aliquota_pct"], "17.5")
        self.assertEqual(aliquota_ir(720)["aliquota_pct"], "17.5")
        self.assertEqual(aliquota_ir(721)["aliquota_pct"], "15.0")

    def test_calcular_ir_comando(self):
        por_dias = calcular_ir_comando("200")
        self.assertEqual(por_dias["aliquota_pct"], "20.0")
        self.assertEqual(por_dias["dias_corridos"], 200)

        por_datas = calcular_ir_comando("2026-01-01", "2026-07-01")
        self.assertEqual(por_datas["dias_corridos"], 181)
        self.assertEqual(por_datas["aliquota_pct"], "20.0")


if __name__ == "__main__":
    unittest.main()
