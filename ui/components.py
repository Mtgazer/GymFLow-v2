import customtkinter as ctk
import config as cfg
from PIL import Image


class SidebarButton(ctk.CTkButton):

    def __init__(
        self,
        parent,
        text,
        icon_path=None,
        command=None,
        active=False
    ):

        image = None

        if icon_path:
            image = ctk.CTkImage(
                Image.open(icon_path),
                size=(20, 20)
            )

        super().__init__(
            parent,

            text=text,
            image=image,
            compound="left",

            command=command,

            height=40,

            corner_radius=2,         

            border_spacing=10,

            anchor="w",

            fg_color=(
                cfg.BUTTON_ACTIVE_COLOR
                if active
                else "transparent"
            ),

            hover_color=cfg.BUTTON_HOVER_COLOR,

            text_color=cfg.TEXT_COLOR,

            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )
class StatCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        title,
        value,
        icon_path=None
    ):

        super().__init__(
            parent,
            fg_color=cfg.CARD_COLOR,
            corner_radius=2,
            height=150
        )

        self.build_card(title, value, icon_path)

    def build_card(self, title, value, icon_path):

        self.pack_propagate(False)

        # ---------- Top Row ----------
        self.top_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.top_frame.pack(
            fill="x",
            padx=20,
            pady=(18,10)
        )

        self.title_label = ctk.CTkLabel(
            self.top_frame,
            text=title,
            font=ctk.CTkFont(
                size=15
            ),
            text_color=cfg.SECONDARY_TEXT
        )

        self.title_label.pack(
            side="left"
        )

        if icon_path:

            self.icon = ctk.CTkImage(
                Image.open(icon_path),
                size=(20,20)
            )

            self.icon_label = ctk.CTkLabel(
                self.top_frame,
                image=self.icon,
                text=""
            )

            self.icon_label.pack(
                side="right"
            )

        # ---------- Value ----------

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            ),
            text_color=cfg.TEXT_COLOR
        )

        self.value_label.pack(
            anchor="w",
            padx=20
        )

class SubscriptionCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        name,
        plan,
        status,
        end_date
    ):

        super().__init__(
            parent,
            fg_color=cfg.CARD_COLOR,
            corner_radius=2,
            height=90
        )

        self.configure(height=90)
        self.pack_propagate(False)

        self.build_card(
            name,
            plan,
            status,
            end_date
        )
    def build_card(
        self,
        name,
        plan,
        status,
        end_date
    ):


        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.header_frame.pack(
            fill="x",
            padx=20,
            pady=(12,4)
        )

        self.name = ctk.CTkLabel(
            self.header_frame,
            text=name,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        )

        self.name.pack(
            side="left"
        )

        status_color = {
            "Paid": "#22C55E",
            "Pending": "#F59E0B",
            "Cancelled": "#EF4444"
        }.get(status, cfg.TEXT_COLOR)

        self.status = ctk.CTkLabel(
            self.header_frame,
            text=status,
            text_color=status_color,
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            )
        )

        self.status.pack(
            side="right",
            padx=(0,10)
        )
        
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.content_frame.pack(
            fill="x",
            padx=20
        )
        self.info_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        self.plan = ctk.CTkLabel(
            self.info_frame,
            text=f"{plan} Membership",
            text_color=cfg.SECONDARY_TEXT
        )

        self.date = ctk.CTkLabel(
            self.info_frame,
            text=f"Expires: {end_date}",
            text_color=cfg.SECONDARY_TEXT,
            font=ctk.CTkFont(size=12)
        )


        self.info_frame.pack(
            fill="x"
        )
        

        self.plan.pack(
            side="left"
        )

        self.date.pack(
            side="right"
        )

class MemberCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        member_id,
        name,
        phone,
        plan,
        expiry,
        edit_callback,
        renew_callback,
        delete_callback
    ):
        
        super().__init__(
            parent,
            fg_color=cfg.CARD_COLOR,
            corner_radius=2,
            height=170
        )

        self.pack_propagate(False)

        self.build_card(
            member_id,
            name,
            phone,
            plan,
            expiry,
            edit_callback,
            renew_callback,
            delete_callback
        )

    def build_card(
        self,
        member_id,
        name,
        phone,
        plan,
        expiry,
        edit_callback,
        renew_callback,
        delete_callback
        ):

        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.header_frame.pack(
            fill="x",
            padx=20,
            pady=(15,8)
        )
        
        self.name = ctk.CTkLabel(
            self.header_frame,
            text=name,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )

        )

        self.name.pack(
            side="left"
        )

        plan_color= {
                "Basic": "#9CA3AF",
                "Premium": "#FACC15",
                "Gold": "#EAB308"
        }.get(plan, cfg.TEXT_COLOR)
        
        self.plan = ctk.CTkLabel(
            self.header_frame,
            text=plan,
            text_color=plan_color,
            font=ctk.CTkFont(
            size=13,
            weight="bold"
            )
        )

        self.plan.pack(
            side="right"
        )
        
        self.info_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.info_frame.pack(
            fill="x",
            padx=20
        )

        phone_label = ctk.CTkLabel(
            self.info_frame,
            text=f"📞 {phone}",
            text_color=cfg.SECONDARY_TEXT,
            font=ctk.CTkFont(
                size=13
            )
        )
        
        phone_label.pack(
            anchor="w"
        )
        
        expiry_label = ctk.CTkLabel(
            self.info_frame,
            text=f"Expires: {expiry}",
            text_color=cfg.SECONDARY_TEXT,
            font=ctk.CTkFont(
                size=13
            )
        )

        expiry_label.pack(
            anchor="w",
            pady=(2,0)
        )

        self.actions = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.actions.pack(
            fill="x",
            padx=20,
            pady=(12,15)
        )

        edit_btn = ctk.CTkButton(
            self.actions,
            text="Edit",
            width=80,
            height=32,
            
            fg_color="#374151",
            hover_color="#4B5563",
            
            text_color="white",
            
            corner_radius=2,

            command=lambda: edit_callback(member_id)
        )

        edit_btn.pack(
            side="left"
        )

        renew_btn = ctk.CTkButton(
            self.actions,
            text="Renew",
            width=90,
            height=32,

            fg_color="#3F6212",
            hover_color="#4D7C0F",
            
            text_color="#D9F99D",

            corner_radius=2,

            command=lambda: renew_callback(member_id)

        )

        renew_btn.pack(
            side="left",
            padx=8
        )

        delete_btn = ctk.CTkButton(
            self.actions,
            text="Delete",

            width=90,
            height=32,

            fg_color="#7F1D1D",
            hover_color="#991B1B",
            text_color="#FECACA",
            
            corner_radius=2,

            command=lambda: delete_callback(
                member_id,
                name)
        )

        delete_btn.pack(
            side="right"
        )