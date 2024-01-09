import re
from pyrogram.client import Client
from pyrogram.enums import ChatMembersFilter
import customtkinter as ctk
from tkinter import messagebox

app = Client("python1")


def is_arabic(text: str):
    return bool(text and re.search(
        '[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\uFDFD\u060C\u061B\u061F\u0660-\u066D\u06EE-\u06EF'
        '\u06C0]+', text, re.IGNORECASE))


def is_arabic_name(full_name: str):
    arabic_names = ['🕌', 'asma', 'Elham', 'Ahlam', 'Asafrah', 'Omran', 'Mehaoud', 'Hamza', 'Hassan',
                    'Ahmed', 'Salem', '🇵🇸', 'Abdullah', '🇾🇪', 'Abuasbeh', 'Mahmoud', 'Fars', 'Rouini', 'Hammad',
                    'Millissa', "☪️", "Mohamed", "🇸🇾", "osama bin laden", "🇩🇿", "størm", "abu ubaidah", "israhell",
                    "Système", "abu ubaida", "Abu Bakar", "🇮🇱💩", "Abu Barjas", "🔻", "hitler"]

    pattern = re.compile('|'.join(re.escape(name) for name in arabic_names), flags=re.IGNORECASE)
    matches = pattern.findall(full_name)
    return bool(matches)


async def scanner(chat_id: int, remove_deleted_user: bool, remove_scam: bool, by_name):
    counter_ban = 0
    async for member in app.get_chat_members(chat_id=chat_id, filter=ChatMembersFilter.SEARCH):
        u_id = member.user.id
        full_name = str(" ".join(filter(None, [member.user.first_name, member.user.last_name])) or None)
        print(full_name)
        if member.user.is_bot:
            continue
        if member.user.is_scam and remove_scam:
            await app.ban_chat_member(chat_id=chat_id, user_id=u_id)
            counter_ban += 1
        elif member.user.is_deleted and remove_deleted_user:
            await app.ban_chat_member(chat_id=chat_id, user_id=u_id)
            counter_ban += 1
        elif is_arabic(full_name):
            await app.ban_chat_member(chat_id=chat_id, user_id=u_id)
            counter_ban += 1
        elif is_arabic_name(full_name) and by_name:
            await app.ban_chat_member(chat_id=chat_id, user_id=u_id)
            counter_ban += 1
        else:
            continue
    return counter_ban


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_position = (screen_width - width) // 2
    y_position = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x_position}+{y_position}")


def start_scanning():
    try:
        chat_id = int(entry_chat_id.get())

        remove_deleted_user = bool(deleted_user.get())
        remove_scam_user = bool(scam_user.get())
        by_name = bool(delete_by_name.get())

        try:
            app.start()
            # Run scanner in a separate thread so that it can be stopped by the user
            counter_ban = app.loop.run_until_complete(scanner(chat_id, remove_deleted_user, remove_scam_user, by_name))
            if counter_ban:
                messagebox.showinfo("Scanning Complete", f"Banned {counter_ban} users.")
            else:
                messagebox.showinfo("Scanning Complete", f"No users found to block.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            app.stop()
    except ValueError:
        messagebox.showerror("Invalid ID", message="The chat ID is invalid")


def on_closing():
    try:
        app.stop()
        root.destroy()
    except ConnectionError:
        root.destroy()


root = ctk.CTk()
root.title("Chat Scanner")
center_window(root, 400, 200)
root.protocol("WM_DELETE_WINDOW", on_closing)

ctk.CTkLabel(root, text="Chat ID:", font=('bold', 20), width=15, height=5).pack()
entry_chat_id = ctk.CTkEntry(root)
entry_chat_id.pack()

deleted_user = ctk.BooleanVar()
deleted_user.set(True)
ctk.CTkCheckBox(root, text="Remove Deleted Users", variable=deleted_user, width=30, height=2, ).pack()

scam_user = ctk.BooleanVar()
scam_user.set(False)
ctk.CTkCheckBox(root, text="Remove Scam Users flagged by Telegram", variable=scam_user, width=30, height=2, ).pack()

delete_by_name = ctk.BooleanVar()
delete_by_name.set(False)
ctk.CTkCheckBox(root, text="Filter by Name (risky)", variable=delete_by_name, width=30, height=2, ).pack()

btn_scan = ctk.CTkButton(root, text="Start Scanning", command=start_scanning)
btn_scan.pack()

root.mainloop()
