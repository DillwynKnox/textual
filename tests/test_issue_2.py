from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Static, Tabs


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

        left = tabs.query_one("#left-indicator", Static)
        right = tabs.query_one("#right-indicator", Static)
        scroll = tabs.query_one("#tabs-scroll")

        
        assert left.parent is tabs
        assert right.parent is tabs
        assert scroll.parent is tabs

       
        children = list(tabs.children)
        assert children.index(left) < children.index(scroll) < children.index(right)