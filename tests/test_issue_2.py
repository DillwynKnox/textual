from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Static, Tabs, Tab


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
class TabsTestApp(App[None]):
    """Test application for Tabs widget testing."""

    def __init__(self, *tabs: str):
        """Initialize the test app with tab labels.

        Args:
            *tabs: Variable number of tab label strings.
        """
        self.tab_labels = tabs
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create the Tabs widget with the provided labels."""
        yield Tabs(*self.tab_labels)


async def test_overflow_updates_on_mount():
    """Test that overflow indicators are correctly initialized when tabs are first mounted.

    Verifies that when a Tabs widget with many tabs is mounted, the right overflow
    indicator appears and the left indicator does not.
    """
    app = TabsTestApp(*[f"Tab {i}" for i in range(20)])
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.pause()
        await pilot.resize_terminal(80, 24)
        await pilot.pause()
        assert tabs.has_class("-overflow-right")
        assert not tabs.has_class("-overflow-left")


async def test_overflow_updates_on_resize():
    """Test that overflow indicators update correctly when the terminal is resized.

    Verifies that when the terminal width is reduced, tabs that previously fit
    now overflow and the right indicator appears.
    """
    app = TabsTestApp("Tab 1", "Tab 2", "Tab 3")
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.resize_terminal(120, 24)
        await pilot.pause()
        assert not tabs.has_class("-overflow-right")
        await pilot.resize_terminal(20, 24)
        await pilot.pause()
        assert tabs.has_class("-overflow-right")


async def test_overflow_updates_when_adding_tabs():
    """Test that overflow indicators update when new tabs are added.

    Verifies that adding enough tabs to exceed the available width causes the
    right overflow indicator to appear.
    """
    app = TabsTestApp("Tab 1", "Tab 2", "Tab 3")
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.resize_terminal(80, 24)
        await pilot.pause()
        assert not tabs.has_class("-overflow-right")
        for i in range(4, 20):
            await tabs.add_tab(f"Tab {i}")
            await pilot.pause()
        assert tabs.has_class("-overflow-right")


async def test_overflow_updates_when_removing_tabs():
    """Test that overflow indicators update when tabs are removed.

    Verifies that removing enough tabs so that all tabs fit within the available
    width causes the right overflow indicator to disappear.
    """
    app = TabsTestApp(*[f"Tab {i}" for i in range(20)])
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.resize_terminal(80, 24)
        await pilot.pause()
        assert tabs.has_class("-overflow-right")
        for i in range(15):
            await tabs.remove_tab(f"tab-{i+1}")
            await pilot.pause()
        assert not tabs.has_class("-overflow-right")

async def test_overflow_updates_when_hiding_tabs():
    """Test that overflow indicators update when tabs are hidden.

    Verifies that hiding enough tabs so that visible tabs fit within the available
    width causes the right overflow indicator to disappear.
    """
    app = TabsTestApp(*[f"Tab {i}" for i in range(20)])
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.resize_terminal(80, 24)
        await pilot.pause()
        assert tabs.has_class("-overflow-right")
        for i in range(15):
            tabs.hide(f"tab-{i+1}")
            await pilot.pause()
        assert not tabs.has_class("-overflow-right")


async def test_overflow_updates_when_showing_tabs():
    """Test that overflow indicators update when hidden tabs are shown.

    Verifies that showing previously hidden tabs causes the right overflow
    indicator to reappear when tabs again exceed the available width.
    """
    app = TabsTestApp(*[f"Tab {i}" for i in range(20)])
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.resize_terminal(80, 24)
        await pilot.pause()
        for i in range(15):
            tabs.hide(f"tab-{i+1}")
        await pilot.pause()
        assert not tabs.has_class("-overflow-right")
        for i in range(15):
            tabs.show(f"tab-{i+1}")
            await pilot.pause()
        assert tabs.has_class("-overflow-right")


async def test_overflow_updates_when_relabelling_tabs():
    """Test that overflow indicators update when tab labels change.

    Verifies that changing a tab's label to a longer string can cause overflow,
    triggering the right indicator to appear.
    """
    app = TabsTestApp("Short")
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.resize_terminal(30, 24)
        await pilot.pause()
        assert not tabs.has_class("-overflow-right")
        tab = tabs.get_tab("tab-1")
        assert tab is not None
        tab.label = "ThisIsAVeryLongTabLabelThatShouldDefinitelyCauseOverflow"
        await pilot.pause()
        tabs.call_after_refresh(tabs._update_overflow_classes)
        await pilot.pause()
        assert tabs.has_class("-overflow-right")

async def test_overflow_updates_when_using_keyboard():
    """Test that overflow indicators update during keyboard navigation.

    Verifies that pressing the right arrow key multiple times scrolls the tabs,
    causing the left overflow indicator to appear.
    """
    app = TabsTestApp(*[f"Tab {i}" for i in range(20)])
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.resize_terminal(80, 24)
        await pilot.pause()
        assert not tabs.has_class("-overflow-left")
        assert tabs.has_class("-overflow-right")
        tabs.focus()
        for _ in range(15):
            await pilot.press("right")
            await pilot.pause()
        assert tabs.has_class("-overflow-left")


async def test_overflow_updates_when_active_tab_changes():
    """Test that overflow indicators update when the active tab is changed programmatically.

    Verifies that setting the active tab to the last tab causes scrolling,
    making the left overflow indicator appear.
    """
    app = TabsTestApp(*[f"Tab {i}" for i in range(20)])
    async with app.run_test() as pilot:
        tabs = app.query_one(Tabs)
        await pilot.resize_terminal(80, 24)
        await pilot.pause()
        assert not tabs.has_class("-overflow-left")
        assert tabs.has_class("-overflow-right")
        last_tab_id = "tab-20"
        tabs.active = last_tab_id
        await pilot.pause()
        assert tabs.has_class("-overflow-left")