import customtkinter as ctk
import config as cfg


class DeleteMemberDialog(ctk.CTkToplevel):

    def __init__(
        self,
        parent,
        member_name,
        confirm_callback
    ):
        super().__init__(parent)

        self.confirm_callback = confirm_callback

        self.title("Delete Member")
        self.geometry("420x220")
        self.resizable(False, False)

        self.configure(
            fg_color=cfg.BACKGROUND_COLOR
        )

        self.grab_set()
        self.focus()

        self.build_ui(member_name)
    
    def build_ui(self, member_name):

        container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        title = ctk.CTkLabel(
            container,
            text="Delete Member",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.pack(
            anchor="w"
        )

        message = ctk.CTkLabel(
            container,
            text=(
                f"Are you sure you want to delete\n"
                f"'{member_name}'?\n\n"
                "This action cannot be undone."
            ),
            justify="left",
            text_color=cfg.SECONDARY_TEXT
        )

        message.pack(
            anchor="w",
            pady=(15,25)
        )

        buttons = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            side="bottom"
        )

        cancel = ctk.CTkButton(
            buttons,
            text="Cancel",
            fg_color="#374151",
            hover_color="#4B5563",
            command=self.destroy,
            corner_radius=2
        )

        cancel.pack(
            side="left"
        )

        delete = ctk.CTkButton(
            buttons,
            text="Delete",
            fg_color="#B91C1C",
            hover_color="#991B1B",
            corner_radius=2,
            command=self.confirm_delete
        )

        delete.pack(
            side="right"
        )
    def confirm_delete(self):

        self.confirm_callback()

        self.destroy()
        