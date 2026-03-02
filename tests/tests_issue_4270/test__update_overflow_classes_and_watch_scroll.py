from __future__ import annotations

import pytest

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Tab, Tabs
from textual.widgets._tabs import Underline

@pytest.fixture(autouse=True)
def fix_tabs_css():
    """There was some error in the CSS in this file, this one temporary fixes it"""
    original = Tabs.DEFAULT_CSS
    Tabs.DEFAULT_CSS = Tabs.DEFAULT_CSS.replace("} _update_overflow_classes", "}")
    yield
    Tabs.DEFAULT_CSS = original

async def test_overflow_classes_has_no_overflow():
    """When all tabs fit, there is no overflow to the left or right"""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("A", "B", "C")

    async with TabsApp().run_test(size=(80, 24)) as pilot:
        tabs = pilot.app.query_one(Tabs)
        await pilot.pause()
        assert not tabs.has_class("-overflow-left")
        assert not tabs.has_class("-overflow-right")


async def test_overflow_classes_with_overflows_when_many_tabs():
    """When 30 tabs overflow a 40-column container, -overflow-right should be set
    and -overflow-left should not."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs(*[f"Tab {i}" for i in range(30)])

    async with TabsApp().run_test(size=(40, 24)) as pilot:
        tabs = pilot.app.query_one(Tabs)
        assert not tabs.has_class("-overflow-left")
        assert tabs.has_class("-overflow-right")


async def test_overflow_classes_after_scrolling():
    """When scrolled all the way to the right, -overflow-left should be set
    and -overflow-right should not."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs(*[f"Tab {i}" for i in range(30)])

    async with TabsApp().run_test(size=(40, 24)) as pilot:
        tabs = pilot.app.query_one(Tabs)
        await pilot.pause()

        scroll = tabs.query_one("#tabs-scroll")
        scroll.scroll_x = scroll.max_scroll_x
        await pilot.pause()

        assert tabs.has_class("-overflow-left")
        assert not tabs.has_class("-overflow-right")

# _watch_scroll

async def test_watch_scroll_no_overflow_at_start():
    """When scroll_x = 0, -overflow-left should not be set since no tabs are 
    hidden to the left, but -overflow-right should be set since 30 tabs 
    overflow the window to the right."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs(*[f"Tab {i}" for i in range(30)])

    async with TabsApp().run_test(size=(40, 24)) as pilot:
        tabs = pilot.app.query_one(Tabs)
        scroll = tabs.query_one("#tabs-scroll")
        await pilot.pause()

        scroll.scroll_x = 0
        await pilot.pause()
        assert not tabs.has_class("-overflow-left")

        #Content to the right
        assert scroll.max_scroll_x > 0


async def test_watch_scroll_both_overflow_in_middle():
    """When scroll_x is in middle, both -overflow-left and 
    -overflow-right should be set, because some tabs are unseen to the left and right."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs(*[f"Tab {i}" for i in range(30)])

    async with TabsApp().run_test(size=(40, 24)) as pilot:
        tabs = pilot.app.query_one(Tabs)
        scroll = tabs.query_one("#tabs-scroll")
        await pilot.pause()

        scroll.scroll_x = scroll.max_scroll_x // 2
        await pilot.pause()
        # Not at start
        assert scroll.scroll_x > 0                        
        assert scroll.scroll_x < scroll.max_scroll_x   

        assert tabs.has_class("-overflow-left")
        assert tabs.has_class("-overflow-right")


async def test_watch_scroll_no_right_overflow_at_end():
    """When scrolled to the end to the right, there should be no right overflow since there are no
    hidden tabs to the right."""

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs(*[f"Tab {i}" for i in range(30)])

    async with TabsApp().run_test(size=(40, 24)) as pilot:
        tabs = pilot.app.query_one(Tabs)
        scroll = tabs.query_one("#tabs-scroll")
        await pilot.pause()

        scroll.scroll_x = scroll.max_scroll_x
        await pilot.pause()
        assert tabs.has_class("-overflow-left")
        assert not tabs.has_class("-overflow-right")

        #At the end
        assert scroll.scroll_x == scroll.max_scroll_x