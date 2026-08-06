import customtkinter as ctk
import config as cfg
from ui.components import StatCard
from ui.components import SubscriptionCard
from datetime import datetime
from services.dashboard_service import DashboardService

class Dashboard(ctk.CTkFrame):

    def __init__(
        self, 
        parent,
        dashboard_service : DashboardService
    ):
        super().__init__(
            parent,
            fg_color=cfg.BACKGROUND_COLOR,
            corner_radius=0
        )

        self.dashboard_service = dashboard_service

        self.build_dashboard()


    def build_dashboard(self):

        self.create_header()

        self.create_statistics()

        self.create_recent_activity()
    
    # ---------- Data ----------

    def get_statistics_data(self):

        return [

            (
                "Members",
                str(self.dashboard_service.get_total_members()),
                "user.png"
            ),

            (
                "Active",
                str(self.dashboard_service.get_active_members()),
                "clipboard.png"
            ),

            (
                "Expired",
                str(self.dashboard_service.get_expired_members()),
                "calendar-days.png"
            ),

            (
                "Revenue",
                f"${self.dashboard_service.get_total_revenue():,.0f}",
                "credit-card.png"
            )

        ]
    
    def get_recent_subscriptions(self):
        return self.dashboard_service.get_recent_subscriptions()
    
    # ---------- UI ----------
    def create_header(self):
        self.header = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=80,

        )

        self.header.pack(
            fill="x",
            padx=30,
            pady=(30,20),
        )

        self.header.pack_propagate(False)

        self.create_left_header()

        self.create_right_header()
    
    def create_left_header(self):

        self.left_header = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        self.left_header.pack(
            side="left",
            fill="y"
        )

        self.title = ctk.CTkLabel(

            self.left_header,
            text="Dashboard",
            font=ctk.CTkFont(
                size=32,
                weight="bold"
            )
        )

        self.title.pack(
            anchor="w"
        )

        self.subtitle = ctk.CTkLabel(
            self.left_header,
            text="Manage members and subscriptions from one place.",
            font=ctk.CTkFont(size=14),
            text_color=cfg.SECONDARY_TEXT
        )

        self.subtitle.pack(
            anchor="w",
            pady=(6,0)
        )
    def create_right_header(self):

        self.right_header = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        self.right_header.pack(
            side="right",
            fill="y"
        )
        
        today = datetime.now()

        weekday= today.strftime("%A")
        date = today.strftime("%d %B %Y")

        self.day_label= ctk.CTkLabel(
            self.right_header,
            text=weekday,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            text_color=cfg.TEXT_COLOR
        )
        self.day_label.pack(
            anchor="e"
        )

        self.date_label = ctk.CTkLabel(
            self.right_header,
            text=date,
            font=ctk.CTkFont(size=13),
            text_color=cfg.SECONDARY_TEXT
        )

        self.date_label.pack(
            anchor="e",
            pady=(4,0)
        )
    def create_statistics(self):

        self.stats_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.stats_frame.pack(
            fill="x",
            padx=30
        )

        self.stats_frame.grid_columnconfigure(
            (0,1,2,3),
            weight=1
        )
        cards = self.get_statistics_data()
        for column, (title, value, icon) in enumerate(cards):

            card = StatCard(
                self.stats_frame,
                title=title,
                value=value,
                icon_path=f"assets/icons/{icon}"
            )

            card.grid(
                row=0,
                column=column,
                padx=10,
                sticky="ew"
            )
 
    def create_recent_activity(self):

        self.recent_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        
        self.recent_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(35,25),
            
        )
        self.cards_container= ctk.CTkFrame(
            self.recent_frame,
            fg_color="transparent",
        )
        self.section_title = ctk.CTkLabel(
            self.recent_frame,
            text="Recent Subscriptions",
            font=ctk.CTkFont(
                size=22,
                weight="bold",

            )
        )

        self.section_title.pack(
            anchor="w",
            pady=(0,15)
        )

        self.cards_container.pack(
            fill="x",
        )



        for subscription in self.get_recent_subscriptions():

            card = SubscriptionCard(
                self.cards_container,
                *subscription
            )

            card.pack(
                fill="x",
                pady=6
            )
    def refresh_dashboard(self):
        
        print("Refreshing dashboard...")

        self.stats_frame.destroy()
        self.recent_frame.destroy()

        self.create_statistics()
        self.create_recent_activity()