import re
import tkinter as tk
from tkinter import messagebox

ALLIES_SPA_TABLE = {
    600: 366,
    575: 350,
    550: 333,
    525: 316,
    500: 300,
    475: 283,
    450: 266,
    425: 250,
    400: 233,
    375: 216,
    350: 200,
    325: 183,
    300: 166,
    275: 150,
    250: 133,
    225: 116,
    200: 100
}

AXIS_SPA_TABLE = {
    500: 366,
    480: 348,
    460: 331,
    440: 313,
    420: 295,
    400: 277,
    380: 260,
    360: 242,
    340: 224,
    320: 206,
    300: 188,
    280: 171,
    260: 153,
    240: 135,
    220: 117,
    200: 100
}

STATIC_ARTY_TABLE = {
    1600: 622,
    1500: 646,
    1400: 670,
    1300: 693,
    1200: 717,
    1100: 741,
    1000: 764,
    900: 788,
    800: 812,
    700: 836,
    600: 859,
    500: 883,
    400: 907,
    300: 930,
    200: 954,
    100: 978
}

ALLIES_SPA_NAME = "M4A3 (105mm)"
AXIS_SPA_NAME = "Sturmpanzer IV"
STATIC_ARTY_NAME = "Static Artillery"

MAX_SPA_MIL = 466
STATIC_ARTY_MIN_METERS = 100
STATIC_ARTY_MAX_METERS = 1600

bg_color = "#0b0f0c"
panel_color = "#111814"
panel_alt = "#152019"
accent = "#00cc66"
text_color = "#d6d6d6"
muted_text = "#9bb5a3"
button_dark = "#1a2420"
button_hover = "#223128"

selected_faction = None
selected_spa_table = None
selected_spa_name = None

root = tk.Tk()
root.title("HLL Calculator")
root.geometry("620x700")
root.configure(bg=bg_color)
root.resizable(False, False)

entry = None
result_text = None
detail_text = None
history_box = None


def interpolate_from_table(value, table):
    if value in table:
        return table[value]

    keys = sorted(table.keys())
    for i in range(len(keys) - 1):
        lower = keys[i]
        upper = keys[i + 1]

        if lower <= value <= upper:
            lower_mil = table[lower]
            upper_mil = table[upper]
            mil = lower_mil + (value - lower) * (upper_mil - lower_mil) / (upper - lower)
            return round(mil)

    return None


def estimate_spa_base_mil(meters, table):
    keys = sorted(table.keys())
    max_chart_meters = keys[-1]
    max_chart_mil = table[max_chart_meters]

    if 0 <= meters <= 200:
        return round((meters / 200) * 100, 2)

    if meters <= max_chart_meters:
        return interpolate_from_table(meters, table)

    second_highest = keys[-2]
    highest = keys[-1]

    meter_step = highest - second_highest
    mil_step = table[highest] - table[second_highest]
    slope = mil_step / meter_step

    mil = max_chart_mil + (meters - max_chart_meters) * slope
    return round(mil)


def parse_spa_input(user_input):
    text = user_input.replace(" ", "")

    if re.fullmatch(r"\d+(\.\d+)?", text):
        meters = float(text)
        return meters, None, None

    match = re.fullmatch(r"(\d+(\.\d+)?)([+-])(\d+(\.\d+)?)", text)
    if not match:
        raise ValueError("Invalid format")

    meters = float(match.group(1))
    operator = match.group(3)
    adjustment = float(match.group(4))

    return meters, operator, adjustment


def parse_static_input(user_input):
    text = user_input.replace(" ", "")
    if not re.fullmatch(r"\d+(\.\d+)?", text):
        raise ValueError("Invalid format")
    return float(text)


def clear_root():
    for widget in root.winfo_children():
        widget.destroy()


def make_title(parent, text, size=22, pady=(0, 8)):
    label = tk.Label(
        parent,
        text=text,
        font=("Arial", size, "bold"),
        fg=text_color,
        bg=bg_color
    )
    label.pack(pady=pady)
    return label


def make_subtitle(parent, text, pady=(0, 12)):
    label = tk.Label(
        parent,
        text=text,
        font=("Arial", 10),
        fg=muted_text,
        bg=bg_color,
        wraplength=560,
        justify="center"
    )
    label.pack(pady=pady)
    return label


def make_button(parent, text, command, primary=False, width=20, height=2):
    return tk.Button(
        parent,
        text=text,
        font=("Arial", 13, "bold"),
        bg=accent if primary else button_dark,
        fg="black" if primary else text_color,
        activebackground=accent if primary else button_hover,
        activeforeground="black" if primary else text_color,
        width=width,
        height=height,
        relief="flat",
        bd=0,
        command=command,
        cursor="hand2"
    )


def show_faction_screen():
    clear_root()

    container = tk.Frame(root, bg=bg_color)
    container.pack(expand=True)

    make_title(container, "HELL LET LOOSE CALCULATOR", 22, pady=(0, 10))
    make_subtitle(container, "Pick a faction", pady=(0, 24))

    make_button(
        container,
        "ALLIES (US)",
        lambda: select_faction("Allies (US)"),
        primary=True,
        width=22
    ).pack(pady=8)

    make_button(
        container,
        "AXIS (GERMAN)",
        lambda: select_faction("Axis (German)"),
        primary=False,
        width=22
    ).pack(pady=8)


def select_faction(faction):
    global selected_faction, selected_spa_table, selected_spa_name

    selected_faction = faction

    if faction == "Allies (US)":
        selected_spa_table = ALLIES_SPA_TABLE
        selected_spa_name = ALLIES_SPA_NAME
    else:
        selected_spa_table = AXIS_SPA_TABLE
        selected_spa_name = AXIS_SPA_NAME

    show_weapon_screen()


def show_weapon_screen():
    clear_root()

    container = tk.Frame(root, bg=bg_color)
    container.pack(expand=True)

    make_title(container, "WEAPON TYPE", 22, pady=(0, 10))
    make_subtitle(container, selected_faction, pady=(0, 24))

    make_button(
        container,
        "SPA",
        show_spa_calculator,
        primary=True,
        width=22
    ).pack(pady=8)

    make_button(
        container,
        "STATIC ARTILLERY",
        show_static_artillery_calculator,
        primary=False,
        width=22
    ).pack(pady=8)

    make_button(
        container,
        "BACK",
        show_faction_screen,
        primary=False,
        width=14,
        height=1
    ).pack(pady=(20, 0))


def show_spa_calculator():
    global entry, result_text, detail_text, history_box

    clear_root()

    container = tk.Frame(root, bg=bg_color, padx=20, pady=20)
    container.pack(fill="both", expand=True)

    make_title(container, "SPA CALCULATOR", 22, pady=(0, 6))
    make_subtitle(container, f"{selected_faction} | {selected_spa_name}", pady=(0, 8))
    make_subtitle(container, "Format: 253+41 or 253-41", pady=(0, 16))

    input_card = tk.Frame(container, bg=panel_color, padx=20, pady=20)
    input_card.pack(fill="x", pady=(0, 16))

    entry = tk.Entry(
        input_card,
        font=("Arial", 26, "bold"),
        width=14,
        justify="center",
        bg=panel_alt,
        fg=accent,
        insertbackground=accent,
        relief="flat",
        bd=0
    )
    entry.pack(pady=(0, 12))
    entry.focus()

    button_row = tk.Frame(input_card, bg=panel_color)
    button_row.pack()

    make_button(
        button_row,
        "CALCULATE",
        convert_spa,
        primary=True,
        width=14,
        height=1
    ).grid(row=0, column=0, padx=6)

    make_button(
        button_row,
        "BACK",
        show_weapon_screen,
        primary=False,
        width=14,
        height=1
    ).grid(row=0, column=1, padx=6)

    result_text = tk.StringVar()
    detail_text = tk.StringVar()

    result_card = tk.Frame(container, bg=panel_color, padx=20, pady=20)
    result_card.pack(fill="x", pady=(0, 16))

    tk.Label(
        result_card,
        textvariable=result_text,
        font=("Arial", 30, "bold"),
        fg=accent,
        bg=panel_color
    ).pack(pady=(0, 8))

    tk.Label(
        result_card,
        textvariable=detail_text,
        font=("Arial", 11),
        fg=text_color,
        bg=panel_color,
        wraplength=540,
        justify="center"
    ).pack()

    history_card = tk.Frame(container, bg=panel_color, padx=16, pady=16)
    history_card.pack(fill="both", expand=True)

    history_header = tk.Frame(history_card, bg=panel_color)
    history_header.pack(fill="x", pady=(0, 8))

    tk.Label(
        history_header,
        text="History",
        font=("Arial", 11, "bold"),
        fg=text_color,
        bg=panel_color
    ).pack(side="left")

    make_button(
        history_header,
        "Clear",
        clear_history,
        primary=False,
        width=10,
        height=1
    ).pack(side="right")

    history_box = tk.Text(
        history_card,
        height=8,
        font=("Consolas", 10),
        bg=panel_alt,
        fg=text_color,
        insertbackground=accent,
        relief="flat",
        bd=0,
        wrap="word"
    )
    history_box.pack(fill="both", expand=True)

    root.bind("<Return>", on_enter_key_spa)


def show_static_artillery_calculator():
    global entry, result_text, detail_text, history_box

    clear_root()

    container = tk.Frame(root, bg=bg_color, padx=20, pady=20)
    container.pack(fill="both", expand=True)

    make_title(container, "STATIC ARTILLERY", 22, pady=(0, 6))
    make_subtitle(container, f"{selected_faction} | {STATIC_ARTY_NAME}", pady=(0, 8))
    make_subtitle(container, "Enter meters only: 100 to 1600", pady=(0, 16))

    input_card = tk.Frame(container, bg=panel_color, padx=20, pady=20)
    input_card.pack(fill="x", pady=(0, 16))

    entry = tk.Entry(
        input_card,
        font=("Arial", 26, "bold"),
        width=14,
        justify="center",
        bg=panel_alt,
        fg=accent,
        insertbackground=accent,
        relief="flat",
        bd=0
    )
    entry.pack(pady=(0, 12))
    entry.focus()

    button_row = tk.Frame(input_card, bg=panel_color)
    button_row.pack()

    make_button(
        button_row,
        "CALCULATE",
        convert_static_artillery,
        primary=True,
        width=14,
        height=1
    ).grid(row=0, column=0, padx=6)

    make_button(
        button_row,
        "BACK",
        show_weapon_screen,
        primary=False,
        width=14,
        height=1
    ).grid(row=0, column=1, padx=6)

    result_text = tk.StringVar()
    detail_text = tk.StringVar()

    result_card = tk.Frame(container, bg=panel_color, padx=20, pady=20)
    result_card.pack(fill="x", pady=(0, 16))

    tk.Label(
        result_card,
        textvariable=result_text,
        font=("Arial", 30, "bold"),
        fg=accent,
        bg=panel_color
    ).pack(pady=(0, 8))

    tk.Label(
        result_card,
        textvariable=detail_text,
        font=("Arial", 11),
        fg=text_color,
        bg=panel_color,
        wraplength=540,
        justify="center"
    ).pack()

    history_card = tk.Frame(container, bg=panel_color, padx=16, pady=16)
    history_card.pack(fill="both", expand=True)

    history_header = tk.Frame(history_card, bg=panel_color)
    history_header.pack(fill="x", pady=(0, 8))

    tk.Label(
        history_header,
        text="History",
        font=("Arial", 11, "bold"),
        fg=text_color,
        bg=panel_color
    ).pack(side="left")

    make_button(
        history_header,
        "Clear",
        clear_history,
        primary=False,
        width=10,
        height=1
    ).pack(side="right")

    history_box = tk.Text(
        history_card,
        height=8,
        font=("Consolas", 10),
        bg=panel_alt,
        fg=text_color,
        insertbackground=accent,
        relief="flat",
        bd=0,
        wrap="word"
    )
    history_box.pack(fill="both", expand=True)

    root.bind("<Return>", on_enter_key_static)


def on_enter_key_spa(event):
    convert_spa()


def on_enter_key_static(event):
    convert_static_artillery()


def convert_spa():
    user_input = entry.get().strip()

    if not user_input:
        return

    try:
        meters, operator, adjustment = parse_spa_input(user_input)

        if meters < 0:
            messagebox.showerror("Out of Range", "Meters cannot be negative.")
            entry.delete(0, tk.END)
            entry.focus()
            return

        base_mil = estimate_spa_base_mil(meters, selected_spa_table)

        if base_mil is None:
            messagebox.showerror("Conversion Error", "Could not calculate mil value.")
            entry.delete(0, tk.END)
            entry.focus()
            return

        if operator:
            if operator == "+":
                final_mil = round(base_mil - adjustment)
                math_line = f"{base_mil:g}mil - {adjustment:g}mil"
            else:
                final_mil = round(base_mil + adjustment)
                math_line = f"{base_mil:g}mil + {adjustment:g}mil"
        else:
            final_mil = round(base_mil)
            math_line = f"{base_mil:g}mil"

        if final_mil < 0:
            messagebox.showerror("Out of Range", "Final mil cannot be negative.")
            entry.delete(0, tk.END)
            entry.focus()
            return

        if final_mil > MAX_SPA_MIL:
            messagebox.showerror(
                "Out of Range",
                f"Final mil is {final_mil:g}, above the max of {MAX_SPA_MIL}."
            )
            entry.delete(0, tk.END)
            entry.focus()
            return

        result_text.set(f"{meters:g} m  ->  {final_mil:g} mil")

        if operator:
            detail_text.set(
                f"{meters:g}m = {base_mil:g}mil\n"
                f"{math_line}\n"
                f"Final = {final_mil:g}mil"
            )
            history_box.insert(
                "end",
                f"{meters:g}m = {base_mil:g}mil | {math_line} | Final = {final_mil:g}mil\n"
            )
        else:
            detail_text.set(
                f"{meters:g}m = {base_mil:g}mil\n"
                f"Final = {final_mil:g}mil"
            )
            history_box.insert(
                "end",
                f"{meters:g}m = {base_mil:g}mil | Final = {final_mil:g}mil\n"
            )

        history_box.see("end")

        entry.delete(0, tk.END)
        entry.focus()

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Enter a value like:\n\n253\n253+41\n253-41"
        )
        entry.delete(0, tk.END)
        entry.focus()


def convert_static_artillery():
    user_input = entry.get().strip()

    if not user_input:
        return

    try:
        meters = parse_static_input(user_input)

        if meters < STATIC_ARTY_MIN_METERS or meters > STATIC_ARTY_MAX_METERS:
            messagebox.showerror(
                "Out of Range",
                f"Enter a value from {STATIC_ARTY_MIN_METERS} to {STATIC_ARTY_MAX_METERS} meters."
            )
            entry.delete(0, tk.END)
            entry.focus()
            return

        mil = round(interpolate_from_table(meters, STATIC_ARTY_TABLE))

        if mil is None:
            messagebox.showerror("Conversion Error", "Could not calculate mil value.")
            entry.delete(0, tk.END)
            entry.focus()
            return

        result_text.set(f"{meters:g} m  ->  {mil:g} mil")
        detail_text.set(
            f"{meters:g}m = {mil:g}mil\n"
            f"Range: {STATIC_ARTY_MIN_METERS}m to {STATIC_ARTY_MAX_METERS}m"
        )
        history_box.insert("end", f"{meters:g}m = {mil:g}mil\n")
        history_box.see("end")

        entry.delete(0, tk.END)
        entry.focus()

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Enter meters only, like:\n\n100\n550\n1600"
        )
        entry.delete(0, tk.END)
        entry.focus()


def clear_history():
    history_box.delete("1.0", "end")


show_faction_screen()
root.mainloop()
