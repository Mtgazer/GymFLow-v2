import customtkinter as ctk
import config as cfg
from services.member_service import MemberService

class EditMemberDialog(ctk.CTkToplevel):

    def __init__(
            self, 
            parent,
            member_service : MemberService,
            member_id,
            refresh_callback
        ):

        super().__init__(parent)

        self.title("Edit Member")

        self.geometry("520x650")

        self.resizable(False, False)

        self.configure(
            fg_color=cfg.BACKGROUND_COLOR
        )

        self.grab_set()

        self.focus()

        self.member_service = member_service

        self.member_id = member_id

        self.refresh_callback = refresh_callback

        self.member = self.member_service.get_member_by_id(self.member_id)

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
            height=70
        )

        header.pack(
            fill="x",
            padx=30,
            pady=(25,20)
        )

        header.pack_propagate(False)

        title= ctk.CTkLabel(
            header,
            text="Edit Member",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            
            )
        )

        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Here you can edit the member info."
        )

        subtitle.pack(anchor="w")

    def create_form(self):

        self.form = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.form.pack(
            fill="x",
            padx=30
        )

        self.create_name()

        self.create_phone()

        self.create_plan()

        self.create_price()

    def create_name(self):
        
        ctk.CTkLabel(
            self.form,
            text="Full Name"

        ).pack(
            anchor="w",
            pady = (0,5)
        )

        self.name_entry = ctk.CTkEntry(
            self.form,
            height=42,
            placeholder_text="Ahmed Ali"
        )

        self.name_entry.pack(
            fill="x",
            pady=(0,15)
        )
    
    def create_phone(self):

        ctk.CTkLabel(
            self.form,
            text="Phone"
        ).pack(
            anchor="w",
            pady=(0,5)
        )

        self.phone_entry = ctk.CTkEntry(
            self.form,
            height=42,
            placeholder_text="010xxxxxxxxx"
        )

        self.phone_entry.pack(
            fill="x",
            pady=(0,15)
        )

    def create_plan(self):

        ctk.CTkLabel(
            self.form,
            text="Membership Plan"
        ).pack(
            anchor="w",
            pady=(0,5)
        )

        self.plan_box = ctk.CTkComboBox(
            self.form,
            height=42,
            values=[
                "Basic",
                "Premium",
                "Gold"
            ]
        )

        self.plan_box.pack(
            fill="x",
            pady=(0,15)
        )

        self.plan_box.set("Premium")

    def create_price(self):

        ctk.CTkLabel(
            self.form,
            text="Price Paid"
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        self.price_entry = ctk.CTkEntry(
            self.form,
            height=42,
            placeholder_text="350"
        )

        self.price_entry.pack(
            fill="x"
        )

    def create_buttons(self):

        buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            side="bottom",
            padx=30,
            pady=30
        )

        cancel = ctk.CTkButton(
            buttons,
            text="Cancel",
            fg_color="#374151",
            command=self.destroy
        )

        cancel.pack(
            side="left"
        )

        save = ctk.CTkButton(
            buttons,
            text="Save Member",
            fg_color=cfg.PRIMARY_COLOR,
            text_color="black",
            command=self.save_changes
        )

        save.pack(
            side="right"
        )
        
    def save_changes(self):

        success, message = self.member_service.edit_member(
            member_id=self.member_id,
            full_name=self.name_entry.get().strip(),
            phone=self.phone_entry.get().strip(),
            plan_name=self.plan_box.get(),
            price_paid=float(self.price_entry.get())
        )

        if not success:
            print(message)
            return

        print(message)

        self.refresh_callback()
        self.destroy()

    def fill_data(self):

        self.name_entry.insert(
            0,
            self.member["full_name"]
        )

        self.phone_entry.insert(
            0,
            self.member["phone"]
        )

        self.plan_box.set(
            self.member["plan_name"]
        )

        self.price_entry.insert(
            0,
            str(self.member["price_paid"])
        )

