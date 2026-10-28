import customtkinter as ctk
import config as cfg
from PIL import Image
from ui.components import SidebarButton


class Sidebar(ctk.CTkFrame):
    
    def __init__(self, parent):
        self.app = parent

        super().__init__(
            parent,
            width=cfg.SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=cfg.SIDEBAR_COLOR,
        )
        
        self.build_sidebar()
    
    def build_sidebar(self):
        self.create_header()
        self.create_navigation()
        self.create_footer()

    def create_header(self):
        self.header_frame = ctk.CTkFrame(
            self,
            height=210,
            fg_color="transparent",
            corner_radius=0,
        )
        self.header_frame.pack(fill="x")
        self.header_frame.propagate(False)

        self.logo = ctk.CTkImage(
            light_image=Image.open("assets/logo/logo_light.png"),
            dark_image=Image.open("assets/logo/logo_dark.png"),
            size=(140, 120),
        )
        self.logo_label = ctk.CTkLabel(
            self.header_frame,
            image=self.logo,
            text="",
        )
        self.logo_label.pack(pady=(25, 5))

    def create_navigation(self):
        self.navigation_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.navigation_frame.pack(
            fill="both",
            expand=True,
            pady=(15, 0),
        )

        self.dashboard_btn = SidebarButton(
            self.navigation_frame,
            text="Dashboard",
            icon_path="assets/icons/house.png",
            command=lambda: self.app.show_page("dashboard"),
            active=True,
        )
        self.dashboard_btn.pack(
            fill="x",
            padx=20,
            pady=5,
        )

        self.subscription_btn = SidebarButton(
            self.navigation_frame,
            text="Members",
            icon_path="assets/icons/members.png",
            command=lambda: self.app.show_page("members"),
            active=False,
        )
        self.subscription_btn.pack(
            fill="x",
            padx=20,
            pady=5,
        )

    def set_active_page(self, page: str):
        """Updates the active button highlighting on page change."""
        if page == "dashboard":
            self.dashboard_btn.configure(fg_color=cfg.BUTTON_ACTIVE_COLOR)
            self.subscription_btn.configure(fg_color="transparent")
        elif page == "members":
            self.dashboard_btn.configure(fg_color="transparent")
            self.subscription_btn.configure(fg_color=cfg.BUTTON_ACTIVE_COLOR)

    def create_footer(self):
        self.footer_frame = ctk.CTkFrame(
            self,
            height=90,
            fg_color="transparent",
            corner_radius=0,
        )
        self.footer_frame.pack(
            fill="x",
            padx=20,
            pady=(10, 20),
        )
        self.footer_frame.propagate(False)
        self.build_footer()
    
    def build_footer(self):
        divider = ctk.CTkFrame(
            self.footer_frame,
            height=1,
            bg_color="#2B313B",
        )
        divider.pack(
            fill="x",
            pady=(0, 25),
        )

        version_label = ctk.CTkLabel(
            self.footer_frame,
            text=f"Version {cfg.APP_VERSION}",
            font=ctk.CTkFont(
                size=12,
                weight="bold",
            ),
            text_color=cfg.SECONDARY_TEXT,
        )
        version_label.pack()

        author_label = ctk.CTkLabel(
            self.footer_frame,
            text=f"© {cfg.CURRENT_YEAR} {cfg.AUTHOR}",
            font=ctk.CTkFont(size=11),
            text_color=cfg.SECONDARY_TEXT,
        )
        author_label.pack(pady=(2, 0))