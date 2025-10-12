from traders import Trader
from typing import List
import asyncio
from tracers import LogTracer
from agents import add_trace_processor
from market import is_market_open
from dotenv import load_dotenv
import os

load_dotenv(override=True)

RUN_EVERY_N_MINUTES = int(os.getenv("RUN_EVERY_N_MINUTES", "60"))
RUN_EVEN_WHEN_MARKET_IS_CLOSED = (
    os.getenv("RUN_EVEN_WHEN_MARKET_IS_CLOSED", "false").strip().lower() == "true"
)
USE_MANY_MODELS = os.getenv("USE_MANY_MODELS", "false").strip().lower() == "true"

styles = ["Patience", "Bold", "Systematic", "Crypto"]
names = ["Warren", "George", "Ray", "Cathie"]

gpt_model_name = os.getenv("GPT_MODEL_NAME", "gpt-4.1-mini")
gpt_model_short_name = os.getenv("GPT_MODEL_SHORT_NAME", "GPT 4.1 Mini")
deepseek_model_name = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
deepseek_model_short_name = os.getenv("DEEPSEEK_MODEL_SHORT_NAME", "DeepSeek V3")
gemini_model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-preview-04-17")
gemini_model_short_name = os.getenv("GEMINI_MODEL_SHORT_NAME", "Gemini 2.5 Flash")
grok_model_name = os.getenv("GROK_MODEL_NAME", "grok-3-mini-beta")
grok_model_short_name = os.getenv("GROK_MODEL_SHORT_NAME", "Grok 3 Mini")
if USE_MANY_MODELS:
    model_names = [
        gpt_model_name,
        deepseek_model_name,
        gemini_model_name,
        grok_model_name
    ]
else:
    model_names = [gpt_model_name] * 4


def create_traders() -> List[Trader]:
    traders = []
    for name, style, model_name in zip(names, styles, model_names):
        traders.append(Trader(name=name, trader_name=style, trader_model_name=model_name))
    return traders

async def run_every_n_minutes():
    add_trace_processor(LogTracer())
    traders = create_traders()
    while True:
        if RUN_EVEN_WHEN_MARKET_IS_CLOSED or is_market_open():
            await asyncio.gather(*[trader.run() for trader in traders])
        else:
            print(f"The Market is closed, sleeping for: {RUN_EVERY_N_MINUTES} minutes")
            await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)


if __name__ == "__main__":
    print(f"Starting scheduler to run every {RUN_EVERY_N_MINUTES} minutes")
    asyncio.run(run_every_n_minutes())