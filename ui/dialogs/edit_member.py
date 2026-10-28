import customtkinter as ctk
import config as cfg
from services.member_service import MemberService


class EditMemberDialog(ctk.CTkToplevel):

    def __init__(
        self,
        parent,
        member_service: MemberService,
        member_id: int,
        refresh_callback,
    ):
        super().__init__(parent)

        self.title("Edit Member")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(fg_color=cfg.BACKGROUND_COLOR)

        self.grab_set()
        self.focus()

        self.member_service = member_service
        self.member_id = member_id
        self.refresh_callback = refresh_callback

        self.member = self.member_service.get_member_by_id(self.member_id)

        self.plan_prices = {
            "Basic": "250",
            "Premium": "350",
            "Gold": "500",
            "VIP Annual": "3500",
        }

        self.build_ui()
        self.fill_data()

    def build_ui(self):
        self.create_header()
        self.create_form()
        self.create_buttons()

    def create_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=70,
        )
        header.pack(fill="x", padx=30, pady=(25, 15))
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="Edit Member",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=cfg.TEXT_COLOR,
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Update member profile and subscription details.",
            text_color=cfg.SECONDARY_TEXT,
            font=ctk.CTkFont(size=13),
        )
        subtitle.pack(anchor="w", pady=(3, 0))

    def create_form(self):
        self.form = ctk.CTkFrame(self, fg_color="transparent")
        self.form.pack(fill="x", padx=30)

        self.error_label = ctk.CTkLabel(
            self.form,
            text="",
            text_color="#EF4444",
            font=ctk.CTkFont(size=12, weight="bold"),
            wraplength=460,
            justify="left",
        )
        self.error_label.pack(anchor="w", pady=(0, 5))

        self.create_name()
        self.create_phone()
        self.create_plan()
        self.create_price()

    def show_error(self, message: str):
        self.error_label.configure(text=f"⚠️ {message}")

    def create_name(self):
        ctk.CTkLabel(
            self.form,
            text="Full Name *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=cfg.TEXT_COLOR,
        ).pack(anchor="w", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            self.form,
            height=42,
            placeholder_text="Ahmed Ali",
            fg_color=cfg.CARD_COLOR,
            border_width=0,
        )
        self.name_entry.pack(fill="x", pady=(0, 15))

    def create_phone(self):
        ctk.CTkLabel(
            self.form,
            text="Phone Number *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=cfg.TEXT_COLOR,
        ).pack(anchor="w", pady=(0, 5))

        self.phone_entry = ctk.CTkEntry(
            self.form,
            height=42,
            placeholder_text="010xxxxxxxxx",
            fg_color=cfg.CARD_COLOR,
            border_width=0,
        )
        self.phone_entry.pack(fill="x", pady=(0, 15))

    def create_plan(self):
        ctk.CTkLabel(
            self.form,
            text="Membership Plan",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=cfg.TEXT_COLOR,
        ).pack(anchor="w", pady=(0, 5))

        self.plan_box = ctk.CTkComboBox(
            self.form,
            height=42,
            values=["Basic", "Premium", "Gold", "VIP Annual"],
            command=self.on_plan_change,
            fg_color=cfg.CARD_COLOR,
            button_color=cfg.PRIMARY_COLOR,
            button_hover_color="#E6B800",
            dropdown_fg_color=cfg.CARD_COLOR,
            border_width=0,
        )
        self.plan_box.pack(fill="x", pady=(0, 15))
        self.plan_box.set("Premium")

    def on_plan_change(self, selected_plan):
        default_price = self.plan_prices.get(selected_plan, "350")
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, default_price)

    def create_price(self):
        ctk.CTkLabel(
            self.form,
            text="Price Paid ($)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=cfg.TEXT_COLOR,
        ).pack(anchor="w", pady=(0, 5))

        self.price_entry = ctk.CTkEntry(
            self.form,
            height=42,
            placeholder_text="350",
            fg_color=cfg.CARD_COLOR,
            border_width=0,
        )
        self.price_entry.pack(fill="x")

    def create_buttons(self):
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", side="bottom", padx=30, pady=25)

        cancel = ctk.CTkButton(
            buttons,
            text="Cancel",
            fg_color="#374151",
            hover_color="#4B5563",
            corner_radius=4,
            command=self.destroy,
        )
        cancel.pack(side="left")

        save = ctk.CTkButton(
            buttons,
            text="Save Changes",
            fg_color=cfg.PRIMARY_COLOR,
            hover_color="#E6B800",
            text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=4,
            command=self.save_changes,
        )
        save.pack(side="right")

    def save_changes(self):
        self.error_label.configure(text="")
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        plan_name = self.plan_box.get()
        raw_price = self.price_entry.get().strip()

        try:
            price = float(raw_price) if raw_price else 0.0
        except ValueError:
            self.show_error("Price paid must be a valid number.")
            return

        success, message = self.member_service.edit_member(
            member_id=self.member_id,
            full_name=name,
            phone=phone,
            plan_name=plan_name,
            price_paid=price,
        )

        if not success:
            self.show_error(message)
            return

        self.refresh_callback()
        self.destroy()

    def fill_data(self):
        if not self.member:
            self.show_error("Could not load member data.")
            return

        self.name_entry.insert(0, self.member.get("full_name", ""))
        self.phone_entry.insert(0, self.member.get("phone", ""))
        plan_name = self.member.get("plan_name") or "Premium"
        self.plan_box.set(plan_name)
        self.price_entry.insert(0, str(self.member.get("price_paid", "350")))
