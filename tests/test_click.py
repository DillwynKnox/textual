from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Tabs


async def test_clicking_indicators_scrolls_tabs() -> None:
    class AppWithTabs(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs(
                "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen"
            )

    async with AppWithTabs().run_test(size=(30, 6)) as pilot:
        tabs = pilot.app.query_one(Tabs)
        scroll = tabs.query_one("#tabs-scroll")

        await pilot.pause()
        start_x = scroll.scroll_x

        # Click Right indicator
        await pilot.click("#right-indicator")
        await pilot.pause()
        assert scroll.scroll_x > start_x

        # Click Left indicator
        mid_x = scroll.scroll_x
        await pilot.click("#left-indicator")
        await pilot.pause()
        assert scroll.scroll_x < mid_x