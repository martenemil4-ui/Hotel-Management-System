
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class HotelError(Exception):
    """Base class for every error raised by the hotel logic."""


class NoRoomAvailableError(HotelError):
    """Raised when a guest asks for a room type that is fully booked."""


class InvalidBookingError(HotelError):
    """Raised for bad input (empty name, days <= 0) or invalid check-out."""


# ----------------------------------------------------------------- rooms
class Rooms:

    room_type = "Room"

    def __init__(self, price, first_room_number, total_rooms):
        self.price = price              
        self.num_room = first_room_number        
        self._total = total_rooms
        self._free = set(range(first_room_number, first_room_number + total_rooms))

    @property
    def total_count(self):
        return self._total

    @property
    def get_available_count(self):
        return len(self._free)

    @property
    def occupied_count(self):
        return self._total - len(self._free)

    @property
    def is_available(self):
        return len(self._free) > 0

    @property
    def all_room_numbers(self):
        return list(range(self.num_room, self.num_room + self._total))

    @property
    def next_room_number(self):
        return min(self._free) if self._free else None

    def is_free(self, room_number):
        return room_number in self._free

    def total_price(self, days):
        return self.price * days

    def book_room(self):
        if not self.is_available:
            raise NoRoomAvailableError(f"No {self.room_type} rooms are available.")
        number = min(self._free)
        self._free.remove(number)
        return number

    def check_out_room(self, room_number):
        """Give a SPECIFIC room number back (never 'last number minus one')."""
        if room_number not in self.all_room_numbers:
            raise InvalidBookingError(f"Room {room_number} is not a {self.room_type} room.")
        if room_number in self._free:
            raise InvalidBookingError(f"Room {room_number} is already free.")
        self._free.add(room_number)


class SingleRoom(Rooms):
    room_type = "Single"

    def __init__(self, price=500, first_room_number=101, total_rooms=10):
        super().__init__(price, first_room_number, total_rooms)


class DoubleRoom(Rooms):
    room_type = "Double"

    def __init__(self, price=700, first_room_number=111, total_rooms=10):
        super().__init__(price, first_room_number, total_rooms)


# --------------------------------------------------------------- booking
class Booking:

    _next_id = 1

    def __init__(self, client_name, num_of_days, room_obj, room_number):
        self.client_name, self.num_of_days = Booking.validate(client_name, num_of_days)
        self.room_obj = room_obj
        self.room_number = room_number
        self.booking_id = Booking._next_id
        Booking._next_id += 1
        self.is_active = True

    @staticmethod
    def validate(client_name, num_of_days):
        name = str(client_name).strip()
        if not name:
            raise InvalidBookingError("Guest name cannot be empty.")
        if isinstance(num_of_days, bool) or not isinstance(num_of_days, int):
            raise InvalidBookingError("Number of days must be a whole number.")
        if num_of_days <= 0:
            raise InvalidBookingError("Number of days must be at least 1.")
        return name, num_of_days

    @property
    def room_type(self):
        return self.room_obj.room_type

    @property
    def price_per_night(self):
        return self.room_obj.price

    @property
    def total_price(self):
        return self.room_obj.total_price(self.num_of_days)

    @property
    def book(self):
        return f"Hello Mr/Miss {self.client_name} You Have Booked {self.num_of_days} Days"

    def close(self):
        if not self.is_active:
            raise InvalidBookingError("This booking was already checked out.")
        self.is_active = False



class Hotel:

    def __init__(self, single_room, dubble_room, resturant, pool):
        self.single_room = single_room
        self.double_room = dubble_room
        self.resturant = resturant
        self.pool = pool
        self.bookings = []          # every booking ever made (active or not)

    # ---- structure
    @property
    def categories(self):
        return {"Single": self.single_room, "Double": self.double_room}

    def get_category(self, room_type):
        try:
            return self.categories[room_type]
        except KeyError:
            raise InvalidBookingError(f"Unknown room type: {room_type}")

    @property
    def show_details(self):
        return (
            f"THIS HOTEL HAS://\n1) {self.single_room.get_available_count} Single Rooms\n2)"
            f" {self.double_room.get_available_count} Double Rooms"
            f"\n3) {self.resturant} Resturants\n4) {self.pool} Pools"
        )

    # ---- bookings
    @property
    def active_bookings(self):
        return [b for b in self.bookings if b.is_active]

    @property
    def names_in_single(self):
        return [b.client_name for b in self.active_bookings if b.room_type == "Single"]

    @property
    def names_in_dubble(self):
        return [b.client_name for b in self.active_bookings if b.room_type == "Double"]

    def book(self, room_type, client_name, days):
        """Validate first, then take a room, then record the booking."""
        name, days = Booking.validate(client_name, days)
        category = self.get_category(room_type)
        number = category.book_room()
        booking = Booking(name, days, category, number)
        self.bookings.append(booking)
        return booking

    def get_booking(self, booking_id):
        for b in self.bookings:
            if b.booking_id == booking_id:
                return b
        raise InvalidBookingError("Booking not found.")

    def booking_in_room(self, room_number):
        for b in self.active_bookings:
            if b.room_number == room_number:
                return b
        return None

    def check_out(self, booking_id):
        """Close the booking and free exactly the room it was using."""
        booking = self.get_booking(booking_id)
        booking.close()                                   # raises if already closed
        booking.room_obj.check_out_room(booking.room_number)
        return booking

    # ---- statistics for the dashboard
    @property
    def total_rooms(self):
        return self.single_room.total_count + self.double_room.total_count

    @property
    def available_rooms(self):
        return self.single_room.get_available_count + self.double_room.get_available_count

    @property
    def occupied_rooms(self):
        return self.total_rooms - self.available_rooms

    @property
    def current_guests(self):
        return len(self.active_bookings)

    @property
    def total_registered_guests(self):
        return len(self.bookings)

    @property
    def occupancy_rate(self):
        return 100 * self.occupied_rooms / self.total_rooms if self.total_rooms else 0


# ------------------------------------------------------------------ theme
NAVY, SIDEBAR = "#0A1228", "#0E1A35"
CARD, CARD2, BORDER = "#15244A", "#1D305F", "#2A4078"
GOLD, GOLD_D = "#D4AF37", "#B8932A"
TEXT, MUTED = "#F2F4F8", "#9AA7C4"
GREEN, RED = "#2FA574", "#D9534F"
DISABLED_BG = "#26345A"
FONT = "Segoe UI"
CURRENCY = "EGP"


def F(size, bold=False):
    return (FONT, size, "bold") if bold else (FONT, size)


def money(value):
    return f"{value:,} {CURRENCY}"


# ---------------------------------------------------- reusable components
class Panel(tk.Frame):
    """Bordered card. Children go into panel.body. Height is never fixed."""

    def __init__(self, parent, title=None, fill=CARD):
        super().__init__(parent, bg=fill, highlightthickness=1, highlightbackground=BORDER)
        if title:
            tk.Label(self, text=title, font=F(11, True), fg=GOLD, bg=fill).pack(
                anchor="w", padx=12, pady=(8, 0))
        self.body = tk.Frame(self, bg=fill)
        self.body.pack(fill="both", expand=True, padx=12, pady=8)


class WrapLabel(tk.Label):
    """Label whose text wraps to the width it is given (never gets cut off)."""

    def __init__(self, parent, **kw):
        super().__init__(parent, justify="left", anchor="w", **kw)
        self.bind("<Configure>", lambda e: self.configure(wraplength=max(e.width - 4, 60)))


def make_button(parent, text, command, primary=True):
    bg, hover, fg = (GOLD, GOLD_D, NAVY) if primary else (CARD2, BORDER, TEXT)
    btn = tk.Button(parent, text=text, command=command, font=F(10, True), bg=bg, fg=fg,
                    activebackground=hover, activeforeground=fg, relief="flat", bd=0,
                    padx=16, pady=6, cursor="hand2", disabledforeground=MUTED,
                    highlightthickness=0)
    btn.normal_bg, btn.hover_bg = bg, hover
    btn.bind("<Enter>", lambda e: btn.cget("state") != "disabled" and btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.cget("state") != "disabled" and btn.configure(bg=bg))
    return btn


def set_enabled(btn, on):
    btn.configure(state="normal" if on else "disabled",
                  bg=btn.normal_bg if on else DISABLED_BG,
                  cursor="hand2" if on else "arrow")


def styled_entry(parent, var):
    return tk.Entry(parent, textvariable=var, font=F(11), bg=CARD2, fg=TEXT,
                    insertbackground=GOLD, relief="flat", highlightthickness=1,
                    highlightbackground=BORDER, highlightcolor=GOLD)


class ProgressBar(tk.Canvas):
    """Horizontal bar that always stretches to the width it is given."""

    def __init__(self, parent, bg=CARD, height=10):
        super().__init__(parent, height=height, bg=bg, highlightthickness=0)
        self._h, self.value = height, 0.0
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, fraction):
        self.value = fraction
        self._draw()

    def _draw(self):
        w = max(self.winfo_width(), 1)
        self.delete("all")
        self.create_rectangle(0, 0, w, self._h, fill=CARD2, outline="")
        if self.value > 0:
            self.create_rectangle(0, 0, max(w * self.value, 6), self._h, fill=GOLD, outline="")


def make_table(parent, columns, height):
    """columns = [(id, title, min_width, anchor)]. Columns stretch to fit the width."""
    holder = tk.Frame(parent, bg=CARD)
    holder.pack(fill="x")
    tree = ttk.Treeview(holder, columns=[c[0] for c in columns], show="headings",
                        height=height, style="Hotel.Treeview", selectmode="browse")
    for cid, title, width, anchor in columns:
        tree.heading(cid, text=title)
        tree.column(cid, width=width, minwidth=40, anchor=anchor, stretch=True)
    sb = ttk.Scrollbar(holder, orient="vertical", command=tree.yview,
                       style="Hotel.Vertical.TScrollbar")
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    tree.pack(side="left", fill="x", expand=True)
    tree.tag_configure("odd", background="#1A2B55")
    tree.tag_configure("even", background=CARD)
    return tree


class ScrollFrame(tk.Frame):
    """Vertical scrolling area. Put content into .inner (it follows the width)."""

    def __init__(self, parent, bg=NAVY):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, yscrollincrement=24)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                 style="Hotel.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", self._on_canvas)

    def _on_inner(self, _e):
        self.canvas.configure(scrollregion=(0, 0, self.inner.winfo_reqwidth(),
                                            self.inner.winfo_reqheight()))

    def _on_canvas(self, e):
        self.canvas.itemconfigure(self._win, width=e.width)

    def to_top(self):
        self.canvas.yview_moveto(0)


class Toast(tk.Frame):
    """Notification at the top-right that disappears by itself."""

    def __init__(self, root):
        super().__init__(root, bg=GREEN)
        self.lbl = tk.Label(self, font=F(10, True), fg="white", padx=14, pady=8, justify="left")
        self.lbl.pack()
        self._job = None

    def show(self, message, ok=True):
        color = GREEN if ok else RED
        self.configure(bg=color)
        self.lbl.configure(text=message, bg=color)
        self.place(relx=1.0, x=-22, y=10, anchor="ne")
        self.lift()
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(3800, self.place_forget)


class NavItem(tk.Frame):
    def __init__(self, parent, text, icon, command):
        super().__init__(parent, bg=SIDEBAR, cursor="hand2")
        self.active = False
        self.bar = tk.Frame(self, bg=SIDEBAR, width=4)
        self.bar.pack(side="left", fill="y")
        self.lbl = tk.Label(self, text=f"{icon}  {text}", font=F(11), fg=MUTED, bg=SIDEBAR,
                            anchor="w", padx=14, pady=9)
        self.lbl.pack(side="left", fill="x", expand=True)
        for w in (self, self.lbl):
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", lambda e: self._paint(True))
            w.bind("<Leave>", lambda e: self._paint(False))

    def set_active(self, on):
        self.active = on
        self._paint(False)

    def _paint(self, hover):
        bg = "#1A2D58" if (self.active or hover) else SIDEBAR
        self.configure(bg=bg)
        self.lbl.configure(bg=bg, fg=GOLD if self.active else (TEXT if hover else MUTED))
        self.bar.configure(bg=GOLD if self.active else bg)


# ------------------------------------------------------------------ pages
class Page(tk.Frame):
    title, subtitle = "", ""

    def __init__(self, parent, app):
        super().__init__(parent, bg=NAVY)
        self.app, self.hotel = app, app.hotel
        tk.Label(self, text=self.title, font=F(17, True), fg=TEXT, bg=NAVY).pack(anchor="w")
        WrapLabel(self, text=self.subtitle, font=F(10), fg=MUTED, bg=NAVY).pack(fill="x")
        tk.Frame(self, bg=GOLD, height=2, width=56).pack(anchor="w", pady=(5, 10))

    def refresh(self):
        pass


class DashboardPage(Page):
    title = "Dashboard"
    subtitle = datetime.now().strftime("Hotel overview  -  %A, %d %B %Y")

    def __init__(self, parent, app):
        super().__init__(parent, app)
        grid = tk.Frame(self, bg=NAVY)
        grid.pack(fill="x")
        defs = [("ts", "Total Single Rooms", "1"), ("td", "Total Double Rooms", "2"),
                ("occ", "Currently Occupied", "\u25CF"),
                ("as", "Available Single Rooms", "\u2713"), ("ad", "Available Double Rooms", "\u2713"),
                ("g", "Total Registered Guests", "\u263A")]
        self.stat = {}
        for i, (key, label, icon) in enumerate(defs):
            grid.columnconfigure(i % 3, weight=1, uniform="stat")
            card = Panel(grid)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=3, pady=3)
            b = card.body
            b.columnconfigure(1, weight=1)
            tk.Label(b, text=icon, font=F(12, True), fg=GOLD, bg=CARD2, width=3).grid(
                row=0, column=0, rowspan=3, padx=(0, 8), sticky="ns")
            val = tk.Label(b, font=F(18, True), fg=TEXT, bg=CARD, anchor="w")
            val.grid(row=0, column=1, sticky="w")
            tk.Label(b, text=label, font=F(9), fg=MUTED, bg=CARD, anchor="w").grid(
                row=1, column=1, sticky="w")
            sub = tk.Label(b, font=F(8), fg=GOLD, bg=CARD, anchor="w")
            sub.grid(row=2, column=1, sticky="w")
            self.stat[key] = (val, sub)

        bottom = tk.Frame(self, bg=NAVY)
        bottom.pack(fill="x", pady=(5, 0))
        bottom.columnconfigure(0, weight=1, uniform="half")
        bottom.columnconfigure(1, weight=1, uniform="half")

        occ = Panel(bottom, "Occupancy")
        occ.grid(row=0, column=0, sticky="nsew", padx=3)
        ob = occ.body
        ob.columnconfigure(1, weight=1)
        self.donut = tk.Canvas(ob, width=96, height=96, bg=CARD, highlightthickness=0)
        self.donut.grid(row=0, column=0, padx=(0, 12))
        bars = tk.Frame(ob, bg=CARD)
        bars.grid(row=0, column=1, sticky="ew")
        self.bar_lbl, self.bar = {}, {}
        for cat in (self.hotel.single_room, self.hotel.double_room):
            lbl = tk.Label(bars, font=F(9, True), fg=TEXT, bg=CARD, anchor="w")
            lbl.pack(fill="x")
            bar = ProgressBar(bars)
            bar.pack(fill="x", pady=(1, 8))
            self.bar_lbl[cat.room_type], self.bar[cat.room_type] = lbl, bar

        mp = Panel(bottom, "Room map")
        mp.grid(row=0, column=1, sticky="nsew", padx=3)
        mb = mp.body
        self.tiles = {}
        for r, cat in enumerate((self.hotel.single_room, self.hotel.double_room)):
            tk.Label(mb, text=cat.room_type, font=F(9, True), fg=MUTED, bg=CARD,
                     width=7, anchor="w").grid(row=r, column=0, sticky="w")
            for i, num in enumerate(cat.all_room_numbers):
                mb.columnconfigure(i + 1, weight=1, uniform="tile")
                tile = tk.Label(mb, font=F(9, True), width=6, pady=2)
                tile.grid(row=r, column=i + 1, padx=2, pady=2, sticky="ew")
                self.tiles[num] = tile
        legend = tk.Frame(mb, bg=CARD)
        legend.grid(row=2, column=0, columnspan=8, sticky="w", pady=(4, 0))
        tk.Label(legend, text=" ", bg=GOLD, width=3).pack(side="left")
        tk.Label(legend, text=" Occupied   ", font=F(8), fg=MUTED, bg=CARD).pack(side="left")
        tk.Label(legend, text=" ", bg=GREEN, width=3).pack(side="left")
        tk.Label(legend, text=" Available", font=F(8), fg=MUTED, bg=CARD).pack(side="left")

    def refresh(self):
        h = self.hotel
        s, d = h.single_room, h.double_room
        vals = {"ts": (s.total_count, f"{money(s.price)} / night"),
                "td": (d.total_count, f"{money(d.price)} / night"),
                "occ": (h.occupied_rooms, f"of {h.total_rooms} rooms"),
                "as": (s.get_available_count, f"{s.occupied_count} occupied"),
                "ad": (d.get_available_count, f"{d.occupied_count} occupied"),
                "g": (h.total_registered_guests, f"{h.current_guests} currently staying")}
        for key, (v, sub) in vals.items():
            self.stat[key][0].configure(text=str(v))
            self.stat[key][1].configure(text=sub)
        self._draw_donut(h.occupancy_rate)
        for cat in (s, d):
            self.bar_lbl[cat.room_type].configure(
                text=f"{cat.room_type} rooms:  {cat.occupied_count} / {cat.total_count} occupied")
            self.bar[cat.room_type].set(cat.occupied_count / cat.total_count)
        for num, tile in self.tiles.items():
            booking = h.booking_in_room(num)
            if booking:
                tile.configure(text=f"{num}\n{booking.client_name[:5]}", bg=GOLD, fg=NAVY)
            else:
                tile.configure(text=f"{num}\nfree", bg=CARD2, fg=GREEN)

    def _draw_donut(self, pct):
        c = self.donut
        c.delete("all")
        c.create_arc(8, 8, 88, 88, start=0, extent=359.9, style="arc", width=10, outline=CARD2)
        if pct > 0:
            c.create_arc(8, 8, 88, 88, start=90, extent=-min(pct * 3.6, 359.9),
                         style="arc", width=10, outline=GOLD)
        c.create_text(48, 48, text=f"{pct:.0f}%", fill=TEXT, font=F(15, True))


class BookingPage(Page):
    title = "New Booking"
    subtitle = "Choose a room type, enter the guest details and confirm."

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.type_var = tk.StringVar(value="Single")
        self.name_var = tk.StringVar()
        self.days_var = tk.StringVar(value="1")

        row = tk.Frame(self, bg=NAVY)
        row.pack(fill="x")
        row.columnconfigure(0, weight=3, uniform="col")
        row.columnconfigure(1, weight=2, uniform="col")

        form = Panel(row, "Guest & room")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        f = form.body
        tk.Label(f, text="Room type", font=F(9), fg=MUTED, bg=CARD).pack(anchor="w")
        tiles = tk.Frame(f, bg=CARD)
        tiles.pack(fill="x", pady=(3, 8))
        tiles.columnconfigure(0, weight=1, uniform="t")
        tiles.columnconfigure(1, weight=1, uniform="t")
        self.tiles = {}
        for i, rt in enumerate(("Single", "Double")):
            cat = self.hotel.get_category(rt)
            lbl = tk.Label(tiles, text=f"{rt} Room\n{money(cat.price)} / night",
                           font=F(10, True), cursor="hand2", pady=6)
            lbl.grid(row=0, column=i, sticky="ew", padx=(0, 6) if i == 0 else 0)
            lbl.bind("<Button-1>", lambda e, r=rt: self._select(r))
            self.tiles[rt] = lbl

        tk.Label(f, text="Guest name", font=F(9), fg=MUTED, bg=CARD).pack(anchor="w")
        styled_entry(f, self.name_var).pack(fill="x", ipady=4, pady=(3, 8))
        tk.Label(f, text="Number of days", font=F(9), fg=MUTED, bg=CARD).pack(anchor="w")
        tk.Spinbox(f, from_=1, to=365, textvariable=self.days_var, width=8, font=F(11),
                   bg=CARD2, fg=TEXT, insertbackground=GOLD, buttonbackground=CARD2,
                   relief="flat", highlightthickness=1, highlightbackground=BORDER,
                   highlightcolor=GOLD).pack(anchor="w", ipady=3, pady=(3, 6))
        self.error = WrapLabel(f, text="", font=F(9, True), fg=RED, bg=CARD)
        self.error.pack(fill="x", pady=(0, 6))
        btns = tk.Frame(f, bg=CARD)
        btns.pack(anchor="w")
        self.confirm_btn = make_button(btns, "Confirm Booking", self.confirm)
        self.confirm_btn.pack(side="left")
        make_button(btns, "Clear", self.clear, primary=False).pack(side="left", padx=8)

        summ = Panel(row, "Booking summary", fill=CARD2)
        summ.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        s = summ.body
        self.rows = {}
        for key, label in (("type", "Room type"), ("price", "Price per night"), ("days", "Nights"),
                           ("avail", "Rooms available"), ("next", "Room to be assigned")):
            r = tk.Frame(s, bg=CARD2)
            r.pack(fill="x", pady=2)
            tk.Label(r, text=label, font=F(10), fg=MUTED, bg=CARD2).pack(side="left")
            v = tk.Label(r, font=F(10, True), fg=TEXT, bg=CARD2)
            v.pack(side="right")
            self.rows[key] = v
        tk.Frame(s, bg=GOLD, height=1).pack(fill="x", pady=6)
        tk.Label(s, text="Total price", font=F(10), fg=MUTED, bg=CARD2).pack(anchor="w")
        self.total = tk.Label(s, font=F(20, True), fg=GOLD, bg=CARD2)
        self.total.pack(anchor="w")

        self.days_var.trace_add("write", lambda *_: self._update())
        self._select("Single")

    def _select(self, room_type):
        self.type_var.set(room_type)
        for rt, lbl in self.tiles.items():
            on = rt == room_type
            lbl.configure(bg=GOLD if on else CARD2, fg=NAVY if on else TEXT)
        self._update()

    def _days(self):
        try:
            return int(self.days_var.get().strip())
        except ValueError:
            return None

    def _update(self):
        cat = self.hotel.get_category(self.type_var.get())
        days = self._days()
        ok_days = days is not None and days > 0
        self.rows["type"].configure(text=f"{cat.room_type} Room")
        self.rows["price"].configure(text=money(cat.price))
        self.rows["days"].configure(text=str(days) if ok_days else "-")
        self.rows["avail"].configure(text=f"{cat.get_available_count} of {cat.total_count}",
                                     fg=TEXT if cat.is_available else RED)
        self.rows["next"].configure(text=str(cat.next_room_number) if cat.is_available
                                    else "Fully booked")
        self.total.configure(text=money(cat.total_price(days)) if ok_days else "-")
        set_enabled(self.confirm_btn, cat.is_available)
        if not cat.is_available:
            self.error.configure(text=f"No {cat.room_type} rooms are available right now.")
        elif self.error.cget("text").startswith("No "):
            self.error.configure(text="")

    def clear(self):
        self.name_var.set("")
        self.days_var.set("1")
        self.error.configure(text="")
        self._update()

    def confirm(self):
        try:
            days = int(self.days_var.get().strip())
        except ValueError:
            self._fail("Number of days must be a whole number.")
            return
        try:
            b = self.hotel.book(self.type_var.get(), self.name_var.get(), days)
        except HotelError as err:
            self._fail(str(err))
            return
        self.app.toast.show(f"Booking confirmed  -  Room {b.room_number}\n"
                            f"{b.client_name}, {b.num_of_days} night(s), {money(b.total_price)}")
        self.clear()
        self.app.refresh_all()

    def _fail(self, message):
        self.error.configure(text=message)
        self.app.toast.show(message, ok=False)

    def refresh(self):
        self._update()


class CheckoutPage(Page):
    title = "Check-out"
    subtitle = "Select an active booking below, then confirm the check-out."

    FIELDS = (("name", "Guest"), ("type", "Room type"), ("room", "Room number"),
              ("days", "Duration"), ("total", "Total bill"))

    def __init__(self, parent, app):
        super().__init__(parent, app)


        top = Panel(self, "Selected booking")
        top.pack(fill="x", pady=(0, 8))
        b = top.body
        self.vals = {}
        for i, (key, label) in enumerate(self.FIELDS):
            b.columnconfigure(i, weight=1, uniform="f")
            tk.Label(b, text=label, font=F(9), fg=MUTED, bg=CARD).grid(row=0, column=i, sticky="w")
            v = tk.Label(b, text="-", font=F(11, True), fg=TEXT, bg=CARD)
            v.grid(row=1, column=i, sticky="w")
            self.vals[key] = v
        bar = tk.Frame(b, bg=CARD)
        bar.grid(row=2, column=0, columnspan=len(self.FIELDS), sticky="ew", pady=(8, 0))
        self.btn = make_button(bar, "Confirm Check-out", self.check_out)
        self.btn.pack(side="right")
        self.hint = WrapLabel(bar, font=F(9), fg=MUTED, bg=CARD)
        self.hint.pack(side="left", fill="x", expand=True)

        lst = Panel(self, "Active bookings")
        lst.pack(fill="x")
        self.tree = make_table(lst.body, [("id", "ID", 40, "center"), ("name", "Guest", 140, "w"),
                                          ("type", "Type", 70, "center"), ("room", "Room", 60, "center"),
                                          ("days", "Days", 50, "center"), ("total", "Total", 100, "center")],
                               height=7)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._show_details())
        self.refresh()

    def refresh(self):
        keep = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        for i, b in enumerate(self.hotel.active_bookings):
            self.tree.insert("", "end", iid=str(b.booking_id), tags=("odd" if i % 2 else "even",),
                             values=(b.booking_id, b.client_name, b.room_type, b.room_number,
                                     b.num_of_days, money(b.total_price)))
        if keep and self.tree.exists(keep[0]):
            self.tree.selection_set(keep[0])
        self._show_details()

    def _selected(self):
        sel = self.tree.selection()
        return self.hotel.get_booking(int(sel[0])) if sel else None

    def _show_details(self):
        b = self._selected()
        if b is None:
            for v in self.vals.values():
                v.configure(text="-", fg=TEXT)
            self.hint.configure(text="No active bookings. Book a room first."
                                if not self.hotel.active_bookings
                                else "Select a guest from the list to enable check-out.")
            set_enabled(self.btn, False)
            return
        self.vals["name"].configure(text=b.client_name)
        self.vals["type"].configure(text=f"{b.room_type} Room")
        self.vals["room"].configure(text=str(b.room_number))
        self.vals["days"].configure(text=f"{b.num_of_days} night(s)")
        self.vals["total"].configure(text=money(b.total_price), fg=GOLD)
        self.hint.configure(text=f"Room {b.room_number} becomes available again after check-out.")
        set_enabled(self.btn, True)

    def check_out(self):
        b = self._selected()
        if b is None:
            self.app.toast.show("Select a booking first.", ok=False)
            return
        if not messagebox.askyesno("Confirm check-out",
                                   f"Check out {b.client_name} from room {b.room_number}?",
                                   parent=self.app):
            return
        try:
            self.hotel.check_out(b.booking_id)
        except HotelError as err:
            self.app.toast.show(str(err), ok=False)
        else:
            self.app.toast.show(f"Check-out complete  -  Room {b.room_number} is available again.")
        self.app.refresh_all()


class GuestsPage(Page):
    title = "Guests & Bookings"
    subtitle = "Everyone currently staying at the hotel."

    def __init__(self, parent, app):
        super().__init__(parent, app)
        bar = tk.Frame(self, bg=NAVY)
        bar.pack(fill="x", pady=(0, 6))
        tk.Label(bar, text="Search", font=F(10), fg=MUTED, bg=NAVY).pack(side="left")
        self.search = tk.StringVar()
        styled_entry(bar, self.search).pack(side="left", padx=8, ipady=3)
        self.count = tk.Label(bar, font=F(10, True), fg=GOLD, bg=NAVY)
        self.count.pack(side="right")
        self.search.trace_add("write", lambda *_: self.refresh())
        card = Panel(self)
        card.pack(fill="x")
        self.tree = make_table(card.body, [
            ("id", "ID", 40, "center"), ("name", "Guest", 120, "w"), ("type", "Room type", 70, "center"),
            ("room", "Room no.", 65, "center"), ("days", "Days", 45, "center"),
            ("price", "Per night", 85, "center"), ("details", "Booking details", 190, "w")], height=10)

    def refresh(self):
        q = self.search.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        shown = 0
        for b in self.hotel.active_bookings:
            if q and q not in b.client_name.lower() and q not in str(b.room_number):
                continue
            self.tree.insert("", "end", tags=("odd" if shown % 2 else "even",), values=(
                b.booking_id, b.client_name, b.room_type, b.room_number, b.num_of_days,
                money(b.price_per_night),
                f"{b.num_of_days} x {b.price_per_night} = {money(b.total_price)}"))
            shown += 1
        self.count.configure(text=f"{shown} guest(s)")



class HotelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grand Royal Hotel  -  Management System")
        self.configure(bg=NAVY)
        self._fit_to_screen()
        self.hotel = Hotel(SingleRoom(), DoubleRoom(), 2, 5)
        self._styles()

        body = tk.Frame(self, bg=NAVY)
        body.pack(fill="both", expand=True)

        side = tk.Frame(body, bg=SIDEBAR, width=180)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(side, text=f"Restaurants: {self.hotel.resturant}    Pools: {self.hotel.pool}",
                 font=F(9), fg=MUTED, bg=SIDEBAR).pack(side="bottom", pady=(0, 10))
        tk.Label(side, text="Data is kept in memory\nand resets when the app closes.",
                 font=F(8), fg=MUTED, bg=SIDEBAR).pack(side="bottom", pady=(0, 6))
        tk.Label(side, text="GRAND ROYAL", font=("Georgia", 15, "bold"), fg=GOLD,
                 bg=SIDEBAR).pack(pady=(16, 0))
        tk.Label(side, text="H O T E L", font=("Georgia", 9), fg=MUTED, bg=SIDEBAR).pack(pady=(0, 14))

        self.scroll = ScrollFrame(body)
        self.scroll.pack(side="left", fill="both", expand=True)
        self.scroll.inner.columnconfigure(0, weight=1)

        self.pages, self.nav = {}, {}
        for key, text, icon, cls in (("dash", "Dashboard", "\u25A6", DashboardPage),
                                     ("book", "New Booking", "\u271A", BookingPage),
                                     ("guests", "Guests & Bookings", "\u2630", GuestsPage),
                                     ("out", "Check-out", "\u21C4", CheckoutPage)):
            item = NavItem(side, text, icon, lambda k=key: self.show_page(k))
            item.pack(fill="x")
            self.nav[key] = item
            self.pages[key] = cls(self.scroll.inner, self)

        self.toast = Toast(self)
        self.bind_all("<MouseWheel>", self._wheel)       
        self.bind_all("<Button-4>", self._wheel)         
        self.bind_all("<Button-5>", self._wheel)
        self.refresh_all()
        self.show_page("dash")

    def _fit_to_screen(self):
        """Size the window from the real screen size (works at 1366x768 and smaller)."""
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1240, sw - 20), min(720, sh - 90)      
        self.geometry(f"{w}x{h}+{max((sw - w) // 2, 0)}+{max((sh - h) // 2 - 20, 0)}")
        self.minsize(min(820, w), min(480, h))
        if sw <= 1440:                                     
            try:
                self.state("zoomed")
            except tk.TclError:
                pass

    def _styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.layout("Hotel.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        s.configure("Hotel.Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
                    rowheight=28, borderwidth=0, font=F(10))
        s.map("Hotel.Treeview", background=[("selected", GOLD)], foreground=[("selected", NAVY)])
        s.configure("Hotel.Treeview.Heading", background=CARD2, foreground=GOLD, relief="flat",
                    font=F(10, True), padding=5)
        s.map("Hotel.Treeview.Heading", background=[("active", "#27427F")])
        s.configure("Hotel.Vertical.TScrollbar", background=CARD2, troughcolor=NAVY,
                    bordercolor=NAVY, arrowcolor=GOLD, lightcolor=CARD2, darkcolor=CARD2)

    def _wheel(self, e):
        w = self.winfo_containing(e.x_root, e.y_root)
        if isinstance(w, ttk.Treeview) and w.yview() != (0.0, 1.0):
            return                                         
        num = getattr(e, "num", 0)
        step = -1 if (num == 4 or (num != 5 and getattr(e, "delta", 0) > 0)) else 1
        self.scroll.canvas.yview_scroll(step * 2, "units")

    def show_page(self, key):
        for k, page in self.pages.items():
            if k == key:
                page.grid(row=0, column=0, sticky="nsew", padx=16, pady=12)
            else:
                page.grid_remove()          
            self.nav[k].set_active(k == key)
        self.pages[key].refresh()
        self.scroll.to_top()

    def refresh_all(self):
        for page in self.pages.values():
            page.refresh()


if __name__ == "__main__":
    HotelApp().mainloop()
