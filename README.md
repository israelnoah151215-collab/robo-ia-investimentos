# Robô IA V2 — Mercado real + Paper Trading

Esta versão usa dados de mercado obtidos no servidor através de `yfinance`/Yahoo Finance e executa somente decisões virtuais. Não existe conexão com corretora e nenhuma ordem real é enviada.

## O que existe
- Ações brasileiras no formato Yahoo (`PETR4.SA`, `VALE3.SA`, etc.)
- Histórico de 2 anos
- Indicadores: SMA20, SMA60, RSI, momentum e volatilidade
- Modelo de classificação Logistic Regression
- Separação temporal treino/teste
- Sinal COMPRA/VENDA/NEUTRO
- Painel web responsivo
- Paper trading como conceito/infraestrutura inicial

## Como executar

Instale Python 3.11+.

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Depois abra:
`http://127.0.0.1:8000`

Em outro dispositivo na mesma rede, use o IP do computador, por exemplo:
`http://192.168.0.10:8000`

## Observações sobre os dados

O pacote yfinance documenta acesso a dados do Yahoo Finance e métodos de histórico. A disponibilidade e o intervalo dos dados dependem do ativo e da fonte. Para operação real, deve-se usar uma fonte/feed apropriado e verificar licenças, latência, qualidade e custos.

## O que ainda NÃO é
- Não é um robô de execução real.
- Não é garantia de lucro.
- Não é recomendação de compra/venda.
- Não inclui custos de corretagem, emolumentos, spread e slippage de execução real.
- Não deve ser usado como base para enviar ordens reais sem validação adicional.

## Próxima etapa
Adicionar um motor de paper trading persistente:
- carteira virtual por usuário;
- ordens virtuais;
- caixa;
- posições;
- P&L realizado/não realizado;
- custos simulados;
- stop e limite de perda;
- banco PostgreSQL;
- logs de auditoria.

Depois disso, avaliar uma integração com uma corretora/API adequada e os requisitos regulatórios aplicáveis.
