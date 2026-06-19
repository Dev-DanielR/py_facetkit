from facetkit import CliFacet, GuiFacet, ServiceFacet, TuiFacet, WebFacet


class TestCliFacet:
    def test_starts_empty(self):
        facet = CliFacet()
        assert facet.name == "cli"
        assert facet.commands == {}

    def test_add_and_remove_command(self):
        facet = CliFacet()

        def ping():
            """Ping the server."""
            return "ok"

        facet.add_command("ping", ping)
        assert facet.commands["ping"].name == "ping"
        assert facet.commands["ping"].callable is ping
        assert facet.commands["ping"].description == "Ping the server."

        facet.remove_command("ping")
        assert "ping" not in facet.commands

    def test_description_from_dedented_docstring(self):
        facet = CliFacet()

        def status():
            """
            Show application status.
            """
            return "ok"

        facet.add_command("status", status)
        assert facet.commands["status"].description == "Show application status."

    def test_missing_docstring_uses_empty_description(self):
        facet = CliFacet()
        facet.add_command("ping", lambda: None)
        assert facet.commands["ping"].description == ""

    def test_clear(self):
        facet = CliFacet()
        facet.add_command("ping", lambda: None)
        facet.clear()
        assert facet.commands == {}


class TestServiceFacet:
    def test_starts_empty(self):
        facet = ServiceFacet()
        assert facet.name == "service"
        assert facet.tasks == {}
        assert facet.providers == {}

    def test_add_and_remove_task(self):
        facet = ServiceFacet()
        factory = lambda: None

        facet.add_task("worker", factory, interval=5.0)
        assert facet.tasks["worker"].name == "worker"
        assert facet.tasks["worker"].factory is factory
        assert facet.tasks["worker"].interval == 5.0

        facet.remove_task("worker")
        assert "worker" not in facet.tasks

    def test_add_and_remove_provider(self):
        facet = ServiceFacet()
        provider = object()

        facet.add_provider("db", provider)
        assert facet.providers["db"] is provider

        facet.remove_provider("db")
        assert "db" not in facet.providers

    def test_clear(self):
        facet = ServiceFacet()
        facet.add_task("worker", lambda: None)
        facet.add_provider("db", object())
        facet.clear()
        assert facet.tasks == {}
        assert facet.providers == {}


class TestTuiFacet:
    def test_starts_empty(self):
        facet = TuiFacet()
        assert facet.name == "tui"
        assert facet.screens == {}
        assert facet.keybindings == {}
        assert facet.current_screen is None

    def test_add_and_remove_screen(self):
        facet = TuiFacet()
        factory = lambda: None

        facet.add_screen("home", factory, "Home")
        assert facet.screens["home"].name == "home"
        assert facet.screens["home"].factory is factory
        assert facet.screens["home"].title == "Home"

        facet.remove_screen("home")
        assert "home" not in facet.screens

    def test_remove_screen_clears_current_screen(self):
        facet = TuiFacet()
        facet.add_screen("home", lambda: None)
        facet.current_screen = "home"

        facet.remove_screen("home")
        assert facet.current_screen is None

    def test_add_and_remove_keybinding(self):
        facet = TuiFacet()
        handler = lambda: None

        facet.add_keybinding("home:q", "q", handler, screen="home", priority=10)
        binding = facet.keybindings["home:q"]
        assert binding.key == "q"
        assert binding.handler is handler
        assert binding.screen == "home"
        assert binding.priority == 10

        facet.remove_keybinding("home:q")
        assert "home:q" not in facet.keybindings

    def test_clear(self):
        facet = TuiFacet()
        facet.add_screen("home", lambda: None)
        facet.add_keybinding("home:q", "q", lambda: None)
        facet.current_screen = "home"
        facet.clear()
        assert facet.screens == {}
        assert facet.keybindings == {}
        assert facet.current_screen is None


class TestGuiFacet:
    def test_starts_empty(self):
        facet = GuiFacet()
        assert facet.name == "gui"
        assert facet.widgets == {}
        assert facet.menus == {}
        assert facet.toolbars == {}
        assert facet.layouts == {}

    def test_add_and_remove_widget(self):
        facet = GuiFacet()
        factory = lambda: None

        facet.add_widget("sidebar", factory, parent="root", layout_hints={"width": 240})
        widget = facet.widgets["sidebar"]
        assert widget.id == "sidebar"
        assert widget.factory is factory
        assert widget.parent == "root"
        assert widget.layout_hints == {"width": 240}

        facet.remove_widget("sidebar")
        assert "sidebar" not in facet.widgets

    def test_add_and_remove_menu_and_toolbar(self):
        facet = GuiFacet()
        menu_factory = lambda: None
        toolbar_factory = lambda: None

        facet.add_menu("file", menu_factory, parent="menubar")
        facet.add_toolbar("main", toolbar_factory, parent="window")

        assert facet.menus["file"].parent == "menubar"
        assert facet.toolbars["main"].parent == "window"

        facet.remove_menu("file")
        facet.remove_toolbar("main")
        assert facet.menus == {}
        assert facet.toolbars == {}

    def test_add_and_remove_layout(self):
        facet = GuiFacet()
        factory = lambda: None

        facet.add_layout("main", factory, hints={"columns": 2})
        assert facet.layouts["main"].hints == {"columns": 2}

        facet.remove_layout("main")
        assert facet.layouts == {}

    def test_clear(self):
        facet = GuiFacet()
        facet.add_widget("sidebar", lambda: None)
        facet.add_menu("file", lambda: None)
        facet.add_toolbar("main", lambda: None)
        facet.add_layout("main", lambda: None)
        facet.clear()
        assert facet.widgets == {}
        assert facet.menus == {}
        assert facet.toolbars == {}
        assert facet.layouts == {}


class TestWebFacet:
    def test_starts_empty(self):
        facet = WebFacet()
        assert facet.name == "web"
        assert facet.routes == {}
        assert facet.middleware == {}
        assert facet.error_handlers == {}

    def test_add_and_remove_route(self):
        facet = WebFacet()
        handler = lambda: None

        facet.add_route("users", "/users", handler, methods=["GET", "POST"])
        route = facet.routes["users"]
        assert route.path == "/users"
        assert route.methods == ("GET", "POST")
        assert route.handler is handler
        assert route.name == "users"

        facet.remove_route("users")
        assert "users" not in facet.routes

    def test_add_and_remove_middleware(self):
        facet = WebFacet()
        handler = lambda req, nxt: nxt(req)

        facet.add_middleware("auth", handler, priority=100)
        middleware = facet.middleware["auth"]
        assert middleware.name == "auth"
        assert middleware.handler is handler
        assert middleware.priority == 100

        facet.remove_middleware("auth")
        assert facet.middleware == {}

    def test_add_and_remove_error_handler(self):
        facet = WebFacet()
        handler = lambda: None

        facet.add_error_handler(404, handler)
        assert facet.error_handlers["404"].code == 404
        assert facet.error_handlers["404"].handler is handler

        facet.remove_error_handler(404)
        assert facet.error_handlers == {}

    def test_clear(self):
        facet = WebFacet()
        facet.add_route("users", "/users", lambda: None)
        facet.add_middleware("auth", lambda r, n: n(r))
        facet.add_error_handler(500, lambda: None)
        facet.clear()
        assert facet.routes == {}
        assert facet.middleware == {}
        assert facet.error_handlers == {}