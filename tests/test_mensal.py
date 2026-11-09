import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "financas-carteira" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from mensal import (
    calcular_xirr,
    simular_meta,
    conciliar,
    comparar_aportes,
    pesos,
    relatorio,
    ZERO,
)


class TestMensal(unittest.TestCase):
    def test_calcular_xirr_padrao(self):
        fluxos = [
            (date(2026, 1, 1), -10000.0),
            (date(2026, 7, 1), -5000.0),
            (date(2027, 1, 1), 16500.0),
        ]
        taxa = calcular_xirr(fluxos)
        self.assertIsNotNone(taxa)
        # Deve estar em torno de ~11% a 12% a.a.
        self.assertAlmostEqual(taxa, 0.117, places=2)

    def test_calcular_xirr_invalido(self):
        # Apenas saídas, sem retorno
        self.assertIsNone(calcular_xirr([(date(2026, 1, 1), -1000.0)]))
        # Apenas fluxos positivos
        self.assertIsNone(calcular_xirr([(date(2026, 1, 1), 1000.0), (date(2026, 2, 1), 500.0)]))

    def test_simular_meta(self):
        meta = {
            "objetivo": "Aposentadoria",
            "valor_brl": "100000",
            "aporte_mensal_brl": "1000",
            "prazo_meses": 60,
            "base": "nominal",
            "retornos_liquidos_aa_pct": ["10"],
        }
        res = simular_meta(meta, Decimal("20000"))
        self.assertEqual(res["objetivo"], "Aposentadoria")
        self.assertEqual(len(res["cenarios"]), 1)
        cenario = res["cenarios"][0]
        self.assertIn("saldo_no_prazo_brl", cenario)
        self.assertGreater(Decimal(cenario["saldo_no_prazo_brl"]), Decimal("20000"))

    def test_conciliar_posicoes(self):
        posicoes = {
            "PETR4": {"abertura": "100", "custo_total_abertura_brl": "3000.00", "fechamento": "150"}
        }
        movimentos = [
            (date(2026, 11, 5), "compra", "PETR4", Decimal("50"), Decimal("1750.00"))
        ]
        res = conciliar(posicoes, movimentos)
        self.assertEqual(res["PETR4"]["esperado"], "150")
        self.assertEqual(res["PETR4"]["observado"], "150")
        self.assertEqual(res["PETR4"]["diferenca"], "0")
        self.assertEqual(res["PETR4"]["custo_total_brl"], "4750.00")
        self.assertEqual(res["PETR4"]["custo_medio_brl"], "31.666667")

    def test_pesos_alocacao(self):
        saldos = {
            "acoes": Decimal("6000.00"),
            "fiis": Decimal("4000.00"),
        }
        p = pesos(saldos)
        self.assertEqual(p["acoes"], "60.00")
        self.assertEqual(p["fiis"], "40.00")


if __name__ == "__main__":
    unittest.main()
