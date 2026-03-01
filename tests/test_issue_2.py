from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Static, Tabs
from textual.containers import Horizontal


async def test_issue_4270_indicator_widgets_are_composed() -> None:
    """

    Verify:
    - #tabs-left-indicator and #tabs-right-indicator exist
    - They are Static
    - They hang directly from Tabs (same parent as #tabs-scroll)
    - They are before and after #tabs-scroll in the child order
    """

    class TabsApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Tabs("One", "Two", "Three")

    async with TabsApp().run_test() as pilot:
        tabs = pilot.app.query_one(Tabs)

        wrapper = tabs.query_one("#tabs-wrapper", Horizontal)
        
        left = wrapper.query_one("#left-indicator", Static)
        right = wrapper.query_one("#right-indicator", Static)
        scroll = wrapper.query_one("#tabs-scroll")
        
        assert left.parent is wrapper
        assert right.parent is wrapper
        assert scroll.parent is wrapper
        
        children = list(wrapper.children)
        assert children.index(left) < children.index(scroll) < children.index(right)