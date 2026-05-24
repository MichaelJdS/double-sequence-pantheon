from pathlib import Path
from config import (
    STRATEGY_FILE,
    MAX_HISTORY,
    MAX_SIGNALS,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    DEMO_INTERVAL_SECONDS,
)
from core.state import AppState
from core.strategy_loader import StrategyRepository
from core.sequence_engine import SequenceEngine
from services.notifier import TelegramNotifier
from services.data_feed import DemoFeed
from services.api_server import create_app


def build_system():
    repository = StrategyRepository.from_file(STRATEGY_FILE)
    state = AppState(max_history=MAX_HISTORY, max_signals=MAX_SIGNALS)
    notifier = TelegramNotifier(
        bot_token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
    )
    engine = SequenceEngine(
        repository=repository,
        state=state,
        notifier=notifier,
    )
    feed = DemoFeed(
        on_spin=lambda color, source="demo": engine.handle_color(color=color, source=source),
        interval_seconds=DEMO_INTERVAL_SECONDS,
    )
    app = create_app(
        state=state,
        repository=repository,
        engine=engine,
        feed=feed,
    )
    return app, state, repository, engine, feed