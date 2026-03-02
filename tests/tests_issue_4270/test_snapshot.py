from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Tabs
from textual.widgets import Static, Tabs


class TabsApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Tabs(
            "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"
        )

    def on_mount(self) -> None:
        tabs = self.query_one(Tabs)

        
        def show_indicators() -> None:
            tabs.add_class("-overflow-left", "-overflow-right")

        self.call_after_refresh(show_indicators)


def test_tabs_indicators_snapshot(snap_compare) -> None:
    assert snap_compare(TabsApp(), terminal_size=(40, 6))


async def test_tabs_overflow_classes_follow_scroll_position() -> None:
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

       
        assert not tabs.has_class("-overflow-left")

        
        
        assert tabs.has_class("-overflow-right")

       
        scroll.scroll_x = scroll.max_scroll_x
        await pilot.pause()

        assert tabs.has_class("-overflow-left")
        assert not tabs.has_class("-overflow-right")

        
        scroll.scroll_x = 0
        await pilot.pause()

        assert not tabs.has_class("-overflow-left")
        assert tabs.has_class("-overflow-right")


async def test_tabs_indicator_widgets_exist_and_are_static() -> None:
    class AppWithTabs(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("One", "Two", "Three")

    async with AppWithTabs().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)

        left = tabs.query_one("#left-indicator", Static)
        right = tabs.query_one("#right-indicator", Static)

        assert left.id == "left-indicator"
        assert right.id == "right-indicator"
        assert "tabs-indicator" in left.classes
        assert "tabs-indicator" in right.classes