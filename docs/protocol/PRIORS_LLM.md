# LLM-elicited prior formulas: what was obtained

Written by `scripts/summarise_priors.py` from the records under `priors/llm/raw/`. No outcome data is read here.

- Model requested: ['claude-opus-5-5']; model that served: ['claude-opus-5-5']; knowledge cut-off told to the model: 30 September 2017.
- Records: 95 (50 knowledge-only, 45 statistics-informed); valid: 95; failed: 0.
- Requests: 95; re-asked after an answer broke the manual: 0; tokens in / out: 440,635 / 426,847.

## Agreement between draws, between procedures and with the generic formulas

Mean pairwise agreement of the draws (1 = identical formulas); agreement of the two consensus formulas; share of the generic formula's literals kept by the consensus, and share kept with the opposite state.

| panel | asset class | draws K / S | agreement K | agreement S | K vs S | literals K / S / generic | generic kept by K / S | generic reversed by K / S |
|---|---|---|---|---|---|---|---|---|
| monthly | hedge_fund_monthly | 5 / 5 | 0.48 | 0.70 | 0.28 | 40 / 42 / 57 | 0.26 / 0.23 | 0.33 / 0.28 |
| weekly | bonds_gov_ig | 5 / 5 | 0.75 | 0.60 | 0.16 | 41 / 44 / 68 | 0.18 / 0.21 | 0.25 / 0.19 |
| weekly | commodities | 5 / 5 | 0.70 | 0.81 | 0.44 | 43 / 49 / 68 | 0.25 / 0.22 | 0.29 / 0.25 |
| weekly | credit_em_debt | 5 / 5 | 0.72 | 0.80 | 0.39 | 46 / 40 / 68 | 0.22 / 0.13 | 0.38 / 0.35 |
| weekly | equity_developed_exus | 5 / 5 | 0.70 | 0.69 | 0.19 | 42 / 47 / 68 | 0.21 / 0.16 | 0.37 / 0.29 |
| weekly | equity_emerging | 5 / 5 | 0.69 | 0.63 | 0.37 | 44 / 45 / 68 | 0.16 / 0.10 | 0.35 / 0.38 |
| weekly | equity_us_broad | 5 / 5 | 0.64 | 0.77 | 0.28 | 44 / 42 / 68 | 0.22 / 0.10 | 0.35 / 0.37 |
| weekly | equity_us_sectors | 5 / 5 | 0.72 | 0.80 | 0.37 | 37 / 41 / 68 | 0.19 / 0.07 | 0.32 / 0.38 |
| weekly | hedge_fund_daily | 5 / 0 | 0.61 | – | – | 38 / – / 68 | 0.13 / – | 0.32 / – |
| weekly | real_estate | 5 / 5 | 0.83 | 0.72 | 0.29 | 43 / 42 / 68 | 0.16 / 0.07 | 0.38 / 0.34 |
| **mean** | | | 0.69 | 0.72 | 0.31 | | 0.20 / 0.14 | 0.34 / 0.32 |

## Agreement between draws by target

| procedure | return | volatility | large_loss | large_gain |
|---|---|---|---|---|
| K | 0.69 | 0.73 | 0.66 | 0.73 |
| S | 0.73 | 0.80 | 0.69 | 0.72 |

## Consensus formulas (literals given by more than half of the valid draws)

**monthly / hedge_fund_monthly / K** (5 draws)

- return: AP: Mkt_RF high; B: BAMLH0A2HYBEY_CHG high; COM: COMIDX_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USDJPY_RET high; IR: T10Y2Y_CHG high AND TB3MS_CHG NOT high; MC: CFNAI NOT high AND NFCI high; ST: MOM high; TF: PTFSSTK high; V: VIXCLS high
- large_loss: AP: MSCIEM NOT high AND Mkt_RF NOT high; B: BAMLEMCBPIEY_CHG high AND BAMLH0A2HYBEY_CHG high; COM: COMIDX_RET NOT high; ENDG: __target__ NOT high; FX: AUDUSD_RET NOT high AND USDJPY_RET NOT high; IR: TB3MS_CHG NOT high; MC: STLFSI high; ST: MOM NOT high; TF: PTFSSTK high; V: EMVFINCRISES high AND VIXCLS high
- large_gain: AP: MSCIEM high AND Mkt_RF high; B: BAMLEMCBPIEY_CHG NOT high AND BAMLH0A2HYBEY_CHG NOT high; COM: COMIDX_RET high; ENDG: __target__ high; FX: PTFSFX high; IR: T10Y2Y_CHG high; MC: STLFSI high; ST: MOM high; TF: PTFSBD high AND PTFSCOM high; V: VIXCLS high

**monthly / hedge_fund_monthly / S** (5 draws)

- return: AP: MSCIEM high AND Mkt_RF high; B: BAMLEMCBPIEY_CHG high AND BAMLH0A2HYBEY_CHG high; COM: COPPER_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND EURUSD_RET high; IR: T1YFF_CHG high; MC: CFNAI NOT high AND NFCI high; ST: RMW high AND ST_REV NOT high; TF: PTFSIR high; V: EMVFINCRISES high
- large_loss: AP: MSCIEM NOT high AND Mkt_RF NOT high; B: BAMLEMCBPIEY_CHG high AND BAMLHE00EHYIEY_CHG high; COM: COPPER_RET NOT high AND WTI_RET NOT high; ENDG: __target__ NOT high; FX: EURUSD_RET NOT high; IR: TB3MS_CHG high; MC: CFNAI NOT high AND NFCI high; ST: RMW high AND ST_REV NOT high; TF: PTFSIR high; V: EMVFINCRISES high AND VIXCLS high
- large_gain: AP: MSCIEM high; B: BAMLEMCBPIEY_CHG NOT high AND BAMLH0A2HYBEY_CHG NOT high; COM: COPPER_RET high; ENDG: __target__ high; FX: AUDUSD_RET high; IR: T1YFF_CHG NOT high; MC: STLFSI high; ST: RMW NOT high; TF: PTFSIR NOT high; V: VIXCLS high

**weekly / bonds_gov_ig / K** (5 draws)

- return: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: T10Y2Y_CHG high AND T5YFF_CHG high; MC: T10YIE_CHG high; V: VIX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high; COM: DBC_RET NOT high; ENDG: __target__ high; IR: T1YFF_CHG high; MC: STLFSI high; V: EPU high AND VIX high
- large_loss: AP: Mkt_RF high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: DBC_RET high; ENDG: __target__ NOT high; FX: USDJPY_RET high; IR: T10Y2Y_CHG high AND T5YFF_CHG high; MC: T10YIE_CHG high; V: VIX NOT high
- large_gain: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: T1YFF_CHG NOT high AND T5YFF_CHG NOT high AND TB3M_CHG NOT high; MC: CLAIMS_CHG high AND STLFSI high; V: VIX high

**weekly / bonds_gov_ig / S** (5 draws)

- return: AP: EEM_RET high; B: AAA10Y_CHG NOT high AND HYG_RET high; COM: WTI_RET NOT high; ENDG: __target__ high; FX: EURUSD_RET NOT high AND USDJPY_RET high; IR: T5YFF_CHG high AND TB3M_CHG NOT high; MC: NFCI high AND T10YIE_CHG NOT high; V: GVZ NOT high AND OVX high
- volatility: AP: Mkt_RF NOT high; B: EMB_RET NOT high AND HYG_RET NOT high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T10Y2Y_CHG high AND T5YFF_CHG high; MC: NFCI high; V: GVZ high AND VIX high
- large_loss: AP: HML high; B: EMB_RET NOT high; COM: WTI_RET high; ENDG: __target__ NOT high; FX: USD_BROAD_RET NOT high; IR: T10Y2Y_CHG high AND T5YFF_CHG high; MC: STLFSI high AND T10YIE_CHG high; ST: RMW NOT high; V: GVZ high
- large_gain: AP: Mkt_RF high; B: AAA10Y_CHG NOT high AND HYG_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USDJPY_RET high; IR: TB3M_CHG NOT high; MC: NFCI high; V: OVX high AND VIX high

**weekly / commodities / K** (5 draws)

- return: AP: EEM_RET high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: DBC_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USD_BROAD_RET NOT high; IR: T10Y2Y_CHG high; MC: NFCI NOT high AND T10YIE_CHG high; V: OVX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: TB3M_CHG high; MC: STLFSI high; V: GVZ high AND OVX high
- large_loss: AP: EEM_RET NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ NOT high; FX: AUDUSD_RET NOT high AND USD_BROAD_RET high; IR: T10Y2Y_CHG NOT high; MC: STLFSI high AND T10YIE_CHG NOT high; V: OVX high AND VIX high
- large_gain: AP: EEM_RET high; B: EMB_RET high; COM: DBC_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USD_BROAD_RET NOT high; IR: T10Y2Y_CHG high; MC: T10YIE_CHG high; V: OVX high AND VIX NOT high

**weekly / commodities / S** (5 draws)

- return: AP: EEM_RET high AND SMB high; B: BAA10Y_CHG high; COM: DBC_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USD_BROAD_RET NOT high; IR: T1YFF_CHG high; MC: NFCI high AND T10YIE_CHG NOT high; ST: MOM high; V: GVZ high AND OVX high
- volatility: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: T5YFF_CHG NOT high; MC: NFCI high AND T10YIE_CHG NOT high; ST: RMW high; V: GVZ high AND OVX high
- large_loss: AP: SMB NOT high; B: BAA10Y_CHG high; COM: SLV_RET high; FX: AUDUSD_RET NOT high AND USD_BROAD_RET high; IR: T1YFF_CHG NOT high; MC: NFCI high AND T10YIE_CHG NOT high; ST: MOM high; V: GVZ high AND OVX high
- large_gain: AP: EEM_RET high; B: BAA10Y_CHG NOT high AND EMB_RET high; COM: DBC_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USD_BROAD_RET NOT high; IR: T10Y2Y_CHG high; MC: CLAIMS_CHG NOT high AND T10YIE_CHG high; ST: MOM NOT high; V: OVX high

**weekly / credit_em_debt / K** (5 draws)

- return: AP: EEM_RET high AND Mkt_RF high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: WTI_RET high; ENDG: __target__ high; FX: AUDUSD_RET NOT high AND USD_BROAD_RET high; IR: T5YFF_CHG high; MC: NFCI high; ST: MOM NOT high; V: VIX high
- volatility: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ high; FX: AUDUSD_RET NOT high AND USDJPY_RET NOT high; IR: T5YFF_CHG high; MC: STLFSI high; V: OVX high AND VIX high
- large_loss: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ NOT high; FX: USD_BROAD_RET high; IR: T5YFF_CHG high; MC: STLFSI high; V: VIX high
- large_gain: AP: EEM_RET high AND Mkt_RF high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: WTI_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USD_BROAD_RET NOT high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: MOM NOT high; V: VIX high

**weekly / credit_em_debt / S** (5 draws)

- return: AP: Mkt_RF high; B: BAA10Y_CHG high; COM: DBC_RET high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T5YFF_CHG high; MC: NFCI high; ST: MOM high; V: VIX high
- volatility: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: EMB_RET NOT high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T1YFF_CHG high; MC: NFCI high; ST: RMW high; V: GVZ high AND VIX high
- large_loss: AP: EEM_RET NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; ENDG: __target__ NOT high; FX: USD_BROAD_RET high; IR: T10Y2Y_CHG high; MC: NFCI high AND STLFSI high; V: GVZ high AND VIX high
- large_gain: AP: EEM_RET high; B: BAA10Y_CHG high; COM: DBC_RET high; ENDG: __target__ NOT high; FX: USD_BROAD_RET NOT high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: MOM NOT high; V: VIX high

**weekly / equity_developed_exus / K** (5 draws)

- return: AP: Mkt_RF high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: DBC_RET high; ENDG: __target__ high; FX: USD_BROAD_RET NOT high; IR: T10Y2Y_CHG high; MC: NFCI high; ST: MOM NOT high; V: VIX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ high; FX: AUDUSD_RET NOT high AND USDJPY_RET NOT high; MC: STLFSI high; ST: ST_REV high; V: VIX high
- large_loss: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ NOT high; FX: AUDUSD_RET NOT high AND USDJPY_RET NOT high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: MOM NOT high; V: VIX high
- large_gain: AP: EEM_RET high; B: HYG_RET high; COM: DBC_RET high; ENDG: __target__ NOT high; FX: AUDUSD_RET high AND USD_BROAD_RET NOT high; IR: T10Y2Y_CHG high; MC: STLFSI high; ST: MOM NOT high; V: VIX high

**weekly / equity_developed_exus / S** (5 draws)

- return: AP: Mkt_RF high; B: EMB_RET high; COM: SLV_RET NOT high AND WTI_RET high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T5YFF_CHG high; MC: NFCI high; ST: MOM high; V: EPU high AND GVZ NOT high
- volatility: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: TB3M_CHG high; MC: NFCI high; ST: RMW high AND ST_REV NOT high; V: GVZ high AND VIX high
- large_loss: AP: SMB NOT high; COM: DBC_RET NOT high AND SLV_RET high; ENDG: __target__ high; FX: AUDUSD_RET high; IR: T10Y2Y_CHG high; MC: NFCI high AND STLFSI high; ST: RMW NOT high; V: GVZ high AND OVX high
- large_gain: AP: EEM_RET high AND Mkt_RF NOT high; B: HYG_RET NOT high; COM: NATGAS_RET NOT high AND WTI_RET high; ENDG: __target__ NOT high; FX: EURUSD_RET high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: CMA high; V: EPU high AND VIX high

**weekly / equity_emerging / K** (5 draws)

- return: AP: EEM_RET NOT high AND Mkt_RF high; B: BAA10Y_CHG NOT high AND EMB_RET high; COM: DBC_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USD_BROAD_RET NOT high; IR: T5YFF_CHG high; MC: NFCI high; ST: MOM NOT high; V: VIX high
- volatility: AP: EEM_RET NOT high; B: BAA10Y_CHG high AND EMB_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high AND USD_BROAD_RET high; IR: T5YFF_CHG high; MC: STLFSI high; ST: MOM NOT high; V: VIX high
- large_loss: AP: EEM_RET NOT high; B: BAA10Y_CHG high AND EMB_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ NOT high; FX: AUDUSD_RET NOT high AND USD_BROAD_RET high; IR: T5YFF_CHG high; MC: NFCI high; ST: MOM NOT high; V: VIX high
- large_gain: AP: Mkt_RF high; B: EMB_RET high; COM: DBC_RET high; ENDG: __target__ NOT high; FX: AUDUSD_RET high AND USD_BROAD_RET NOT high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: MOM NOT high; V: VIX high

**weekly / equity_emerging / S** (5 draws)

- return: AP: Mkt_RF high; B: HYG_RET high; COM: DBC_RET high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T5YFF_CHG high; MC: NFCI high; ST: RMW high; V: EPU high AND VIX high
- volatility: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: AUDUSD_RET NOT high AND USD_BROAD_RET high; IR: T5YFF_CHG high; MC: NFCI high; ST: RMW high; V: GVZ high AND VIX high
- large_loss: AP: EEM_RET NOT high; B: BAA10Y_CHG high AND EMB_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ NOT high; FX: AUDUSD_RET NOT high AND USD_BROAD_RET high; IR: T10Y2Y_CHG high; MC: NFCI high AND STLFSI high; ST: RMW high; V: GVZ high AND OVX high
- large_gain: AP: Mkt_RF NOT high; B: HYG_RET NOT high; COM: DBC_RET high; ENDG: __target__ NOT high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: RMW high; V: EPU high AND VIX high

**weekly / equity_us_broad / K** (5 draws)

- return: AP: EEM_RET high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: DBC_RET high; ENDG: __target__ high; FX: AUDUSD_RET high AND USDJPY_RET high; IR: T10Y2Y_CHG high; MC: NFCI high; ST: MOM NOT high; V: VIX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: TB3M_CHG NOT high; MC: STLFSI high; ST: ST_REV high; V: VIX high
- large_loss: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ NOT high; FX: AUDUSD_RET NOT high AND USDJPY_RET NOT high; IR: TB3M_CHG NOT high; MC: CLAIMS_CHG high AND NFCI high; ST: MOM NOT high; V: EPU high AND VIX high
- large_gain: AP: EEM_RET high; B: HYG_RET high; COM: DBC_RET high; ENDG: __target__ NOT high; FX: AUDUSD_RET high; IR: T10Y2Y_CHG high; MC: STLFSI high; ST: MOM NOT high; V: VIX high

**weekly / equity_us_broad / S** (5 draws)

- return: AP: Mkt_RF high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET high; ENDG: __target__ high; FX: AUDUSD_RET high; IR: T5YFF_CHG high; MC: NFCI high; ST: CMA high; V: VIX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: T10Y2Y_CHG NOT high; MC: NFCI high AND T10YIE_CHG NOT high; ST: RMW high; V: VIX high
- large_loss: AP: SMB NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ NOT high; FX: USDJPY_RET NOT high; IR: T10Y2Y_CHG high; MC: NFCI high; ST: ST_REV NOT high; V: OVX high AND VIX high
- large_gain: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ NOT high; FX: USDJPY_RET NOT high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: CMA high; V: VIX high

**weekly / equity_us_sectors / K** (5 draws)

- return: AP: Mkt_RF high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: WTI_RET high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T10Y2Y_CHG high AND TB3M_CHG NOT high; MC: NFCI high; ST: MOM high; V: VIX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high; MC: STLFSI high; ST: ST_REV high; V: VIX high
- large_loss: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ NOT high; FX: USDJPY_RET NOT high; MC: NFCI high; ST: MOM NOT high; V: VIX high
- large_gain: B: HYG_RET high; COM: DBC_RET high; ENDG: __target__ NOT high; FX: AUDUSD_RET high; IR: T10Y2Y_CHG high; MC: STLFSI high; ST: ST_REV high; V: VIX high

**weekly / equity_us_sectors / S** (5 draws)

- return: AP: Mkt_RF high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET high; ENDG: __target__ high; IR: T5YFF_CHG high; MC: NFCI high; ST: CMA high; V: VIX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high AND USD_BROAD_RET high; IR: T5YFF_CHG NOT high; MC: NFCI high; ST: RMW high; V: VIX high
- large_loss: AP: SMB NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ NOT high; FX: USDJPY_RET NOT high; MC: NFCI high AND STLFSI high; ST: ST_REV NOT high; V: OVX high AND VIX high
- large_gain: AP: Mkt_RF NOT high; B: HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ NOT high; FX: USD_BROAD_RET high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: CMA high; V: EPU high AND VIX high

**weekly / hedge_fund_daily / K** (5 draws)

- return: AP: Mkt_RF NOT high; B: BAA10Y_CHG high; COM: DBC_RET high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: MOM high; V: VIX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: T5YFF_CHG high; MC: STLFSI high; ST: MOM NOT high; V: GVZ high AND VIX high
- large_loss: AP: Mkt_RF high; B: HYG_RET high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: T5YFF_CHG high; MC: STLFSI high; ST: MOM NOT high AND ST_REV high; V: VIX high
- large_gain: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: MOM high; V: VIX high

**weekly / real_estate / K** (5 draws)

- return: AP: Mkt_RF high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: DBC_RET high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T5YFF_CHG high; MC: NFCI high; ST: ST_REV high; V: VIX high
- volatility: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: WTI_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high; IR: T5YFF_CHG high; MC: NFCI high AND STLFSI high; ST: MOM NOT high; V: EPU high AND VIX high
- large_loss: AP: Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ NOT high; FX: USD_BROAD_RET high; IR: T5YFF_CHG high; MC: STLFSI high; ST: MOM NOT high; V: VIX high
- large_gain: AP: Mkt_RF high; B: BAA10Y_CHG NOT high AND HYG_RET high; COM: DBC_RET high; ENDG: __target__ NOT high; FX: USD_BROAD_RET NOT high; IR: T10Y2Y_CHG NOT high AND T5YFF_CHG NOT high; MC: NFCI high; ST: ST_REV high; V: VIX high

**weekly / real_estate / S** (5 draws)

- return: AP: Mkt_RF high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: SLV_RET high; ENDG: __target__ high; FX: USD_BROAD_RET high; IR: T10Y2Y_CHG high AND T5YFF_CHG high; MC: T10YIE_CHG high; ST: CMA high; V: VIX high
- volatility: AP: EEM_RET NOT high AND Mkt_RF NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: DBC_RET NOT high; ENDG: __target__ high; FX: USDJPY_RET NOT high AND USD_BROAD_RET high; IR: T5YFF_CHG NOT high; MC: NFCI high; ST: RMW high; V: VIX high
- large_loss: AP: SMB NOT high; B: BAA10Y_CHG high AND HYG_RET NOT high; COM: SLV_RET high; ENDG: __target__ NOT high; IR: T10Y2Y_CHG high; MC: NFCI high; ST: RMW high; V: GVZ high AND VIX high
- large_gain: AP: Mkt_RF NOT high; B: BAA10Y_CHG high; COM: DBC_RET NOT high; ENDG: __target__ NOT high; FX: USDJPY_RET NOT high; IR: T5YFF_CHG NOT high; MC: STLFSI high; ST: CMA high; V: VIX high

