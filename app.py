"""GymFlow Main Application Entry Point."""
import customtkinter as ctk
import config as cfg
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.members import Members
from core.container import Container


class GymFlow(ctk.CTk):
    """Main window class for GymFlow GUI application."""

    def __init__(self, container: Container = None):
        super().__init__()

        self.container = container or Container()

        self.setup_theme()
        self.setup_window()
        self.build_ui()

    def setup_window(self):
        self.title(f"{cfg.APP_NAME} - Gym Management System")
        self.geometry(f"{cfg.WINDOW_WIDTH}x{cfg.WINDOW_HEIGHT}")
        self.minsize(1000, 650)

    def build_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self)
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns",
        )

        self.content = ctk.CTkFrame(
            self,
            fg_color=cfg.BACKGROUND_COLOR,
            corner_radius=0,
        )
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
        )
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.dashboard_page = Dashboard(
            parent=self.content,
            dashboard_service=self.container.dashboard_service,
        )

        self.members_page = Members(
            parent=self.content,
            dashboard_page=self.dashboard_page,
            member_service=self.container.member_service,
        )

        self.dashboard_page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.members_page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.show_page("dashboard")

    def show_page(self, page: str):
        if page == "dashboard":
            self.dashboard_page.tkraise()
            self.sidebar.set_active_page("dashboard")
        elif page == "members":
            self.members_page.tkraise()
            self.sidebar.set_active_page("members")

    def setup_theme(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")


def main():
    app = GymFlow()
    app.mainloop()


if __name__ == "__main__":
    main()