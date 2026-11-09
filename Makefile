.PHONY: test demo install install-global clean

test:
	python3 -m unittest discover tests -v

demo:
	@echo "=== 1. Validando plano da carteira ==="
	python3 skills/financas-carteira/scripts/carteira.py plano skills/financas-carteira/references/carteira-exemplo.json
	@echo "\n=== 2. Calculando alíquota de IR regressivo (180 dias) ==="
	python3 skills/financas-carteira/scripts/carteira.py ir 180
	@echo "\n=== 3. Gerando relatório mensal com conciliação e XIRR ==="
	python3 skills/financas-carteira/scripts/mensal.py skills/financas-carteira/references/mensal-exemplo.json skills/financas-carteira/references/movimentos-exemplo.csv

install:
	./install.sh

install-global:
	./install.sh --global

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -delete
