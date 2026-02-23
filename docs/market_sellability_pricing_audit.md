# Market Sellability + Pricing Audit

## Contract Findings

- Primary docs reviewed:
  - `design/market_pricing_contract.md`
  - `design/government_tag_interpretation.md`
  - `design/goods.md`
- Intended behavior (as implemented target):
  - Selling is category-based; explicit SKU listing controls preference tier.
  - Substitutes are sellable only when category exists.
  - Tag interpretation is contextual and deterministic via government policy/tag interpreter.
  - No upper clamp should be applied to final prices (non-negative floor only).

## Call Chain Map (Current Runtime)

- Sell list:
  - `GameEngine._execute_market_sell_list`
  - -> `GameEngine._market_price_rows(action="sell")`
  - -> `GameEngine._market_price_quote(...)`
  - -> `market_pricing.price_transaction(...)`

- Sell action:
  - `GameEngine._execute_market_sell`
  - -> `GameEngine._market_row_by_sku(action="sell", sku_id)`
  - -> `GameEngine._market_price_rows(action="sell")`
  - -> `GameEngine._market_price_quote(...)`
  - -> `market_pricing.price_transaction(...)`

- CLI display path:
  - `run_game_engine_cli._print_market_sku_overlay(...)`
  - -> engine `market_sell_list` rows
  - -> sell price shown when row exists for cargo SKU.

## Alignment vs Gaps (Pre-fix)

- Aligned:
  - Deterministic substitution discount pipeline exists.
  - Market rows come from engine source of truth.
  - Non-negative floor exists; no active upper clamp in runtime path.

- Missing / incorrect:
  - Variant/base family recognition was brittle and non-generic.
  - No near-match tier between exact and substitution.
  - Unknown but valid variants could drop out of sell list.
  - Substitution behavior needed clearer anchoring to sold item base SKU while keeping deterministic modifier pipeline.
