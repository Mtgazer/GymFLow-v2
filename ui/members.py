import customtkinter as ctk
import config as cfg
from ui.components import MemberCard
from ui.dialogs.add_member import AddMemberDialog
from services.member_service import MemberService
from ui.dialogs.edit_member import EditMemberDialog
from ui.dialogs.renew_member import RenewMemberDialog
from ui.dialogs.delete_member import DeleteMemberDialog


class Members(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        dashboard_page,
        member_service: MemberService,
    ):
        super().__init__(
            parent,
            fg_color=cfg.BACKGROUND_COLOR,
            corner_radius=0,
        )

        self.dashboard = dashboard_page
        self.member_service = member_service

        self.build_members()

    def build_members(self):
        self.create_header()
        self.create_toolbar()
        self.create_members_list()

    def create_header(self):
        self.header = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=90,
        )
        self.header.pack(
            fill="x",
            padx=30,
            pady=(30, 20),
        )
        self.header.pack_propagate(False)

        self.left_header = ctk.CTkFrame(
            self.header,
            fg_color="transparent",
        )
        self.left_header.pack(
            side="left",
            fill="y",
        )

        title = ctk.CTkLabel(
            self.left_header,
            text="Members",
            font=ctk.CTkFont(
                size=32,
                weight="bold",
            ),
            text_color=cfg.TEXT_COLOR,
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            self.left_header,
            text="Manage all gym members, subscriptions, and actions.",
            font=ctk.CTkFont(size=14),
            text_color=cfg.SECONDARY_TEXT,
        )
        subtitle.pack(
            anchor="w",
            pady=(4, 0),
        )

    def create_toolbar(self):
        self.toolbar = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=45,
        )
        self.toolbar.pack(
            fill="x",
            padx=30,
            pady=(0, 25),
        )
        self.toolbar.pack_propagate(False)

        self.search_entry = ctk.CTkEntry(
            self.toolbar,
            width=320,
            height=40,
            placeholder_text="Search member by name or phone...",
            fg_color=cfg.CARD_COLOR,
            border_width=0,
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_members)

        # Right-side action buttons: Add Member and Undo Action
        self.add_button = ctk.CTkButton(
            self.toolbar,
            text="+ Add Member",
            command=self.open_add_dialog,
            width=150,
            height=40,
            fg_color=cfg.PRIMARY_COLOR,
            hover_color="#E6B800",
            text_color="black",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
            corner_radius=2,
        )
        self.add_button.pack(side="right")

        # Undo button demonstrating the Stack Data Structure
        self.undo_button = ctk.CTkButton(
            self.toolbar,
            text="↺ Undo",
            command=self.undo_action,
            width=110,
            height=40,
            fg_color="#374151",
            hover_color="#4B5563",
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=2,
        )
        self.undo_button.pack(side="right", padx=(0, 10))
        self.update_undo_button_state()

    def update_undo_button_state(self):
        """Updates the Undo button label and enabled state based on Stack contents."""
        if hasattr(self, "undo_button"):
            if self.member_service.can_undo():
                count = self.member_service.undo_stack.size()
                self.undo_button.configure(
                    state="normal",
                    text=f"↺ Undo ({count})",
                    fg_color="#4B5563",
                )
            else:
                self.undo_button.configure(
                    state="disabled",
                    text="↺ Undo",
                    fg_color="#1F2937",
                )

    def undo_action(self):
        """Executes undo from the LIFO UndoStack and refreshes the view."""
        if self.member_service.can_undo():
            success, message = self.member_service.undo_last_action()
            print(f"[Undo] {message}")
            self.refresh_all()

    def create_members_list(self):
        self.members_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.members_container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 25),
        )
        self.refresh_members()

    def refresh_members(self):
        self.search_members()
        self.update_undo_button_state()

    def open_add_dialog(self):
        AddMemberDialog(
            self,
            self.member_service,
            self.refresh_all,
        )

    def edit_member(self, member_id):
        EditMemberDialog(
            self,
            self.member_service,
            member_id,
            self.refresh_all,
        )

    def ask_delete_member(self, member_id, member_name):
        DeleteMemberDialog(
            self,
            member_name,
            lambda: self.delete_member(member_id),
        )

    def delete_member(self, member_id):
        success = self.member_service.delete_member(member_id)
        if success:
            self.refresh_all()

    def renew_member(self, member_id):
        RenewMemberDialog(
            self,
            self.member_service,
            member_id,
            self.refresh_all,
        )

    def search_members(self, event=None):
        keyword = self.search_entry.get().strip().lower()

        for widget in self.members_container.winfo_children():
            widget.destroy()

        all_members = self.member_service.get_members()
        matched = 0

        for member in all_members:
            if (
                not keyword
                or keyword in member.full_name.lower()
                or keyword in member.phone.lower()
            ):
                matched += 1
                card = MemberCard(
                    self.members_container,
                    member.id,
                    member.full_name,
                    member.phone,
                    member.plan,
                    member.expiry,
                    edit_callback=self.edit_member,
                    renew_callback=self.renew_member,
                    delete_callback=self.ask_delete_member,
                )
                card.pack(
                    fill="x",
                    pady=6,
                )

        if matched == 0:
            empty_label = ctk.CTkLabel(
                self.members_container,
                text="No members found matching your search." if keyword else "No gym members registered yet. Click '+ Add Member' to begin.",
                font=ctk.CTkFont(size=14),
                text_color=cfg.SECONDARY_TEXT,
            )
            empty_label.pack(pady=40)

    def refresh_all(self):
        self.refresh_members()
        self.dashboard.refresh_dashboard()