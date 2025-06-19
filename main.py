
import math
import tkinter as tk
from tkinter import ttk, messagebox
import db

BG_MAIN = "#FFFFFF"
BG_SECOND = "#BBDCFA"
ACCENT = "#0C4882"
FONT_MAIN = ("Constantia", 12)
FONT_SMALL = ("Constantia", 10)

class RaschetMaterial(tk.Frame):
    def __init__(self, parent, return_callback):
        super().__init__(parent, bg=BG_MAIN)
        self.return_callback = return_callback

        tk.Label(self, text="Расчет продукции", font=("Constantia", 14), bg=BG_MAIN).pack(pady=10)

        form = tk.Frame(self, bg=BG_MAIN)
        form.pack(pady=10)

        self.vars = {}
        fields = [
            ("Индентификатор типа продукции", tk.StringVar()),
            ("Индентификатор типа материала", tk.StringVar()),
            ("Количество сырья", tk.StringVar()),
            ("Первый параметр", tk.StringVar()),
            ("Второй параметр", tk.StringVar())
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(form, text=label + ":", font=FONT_MAIN, bg=BG_MAIN).grid(row=i, column=0, sticky="e", pady=2)
            entry = tk.Entry(form, textvariable=var, width=33)
            entry.grid(row=i, column=1, padx=5)
            self.vars[label] = var

        btns = tk.Frame(self, bg=BG_MAIN)
        btns.pack(pady=10)
        tk.Button(btns, text="Расчитать", bg=ACCENT, fg="white", command=self.calculate_product_quantity).pack(side="left", padx=5)
        tk.Button(btns, text="Назад", command=self.return_callback).pack(side="left", padx=5)
    
    def calculate_product_quantity(self):
        try:
            data = {
                "product_type_id": int(self.vars["Индентификатор типа продукции"].get()),
                "material_type_id": int(self.vars["Индентификатор типа материала"].get()),
                "product_quantity": int(self.vars["Количество продуктов"].get()),
                "param1": float(self.vars["Первый параметр"].get()),
                "param2": float(self.vars["Второй параметр"].get()),
            }
            if not isinstance(data["product_type_id"], int) or not isinstance(data["product_type_id"], int) or not isinstance(data["product_quantity"], int):
                raise ValueError("Неправильные данные: -1")
            if data["product_type_id"] < 0 or data["param1"] <= 0 or data["param2"] <= 0:
                raise ValueError("Неправильные данные: -1")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return
        
        try:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT type_coefficient FROM products_type WHERE id_product_type = %s", (data["product_type_id"],))
            product_result = cursor.fetchone()
            if not product_result:
                cursor.close()
                conn.close()
                messagebox.showerror("Ошибка", "Некорректные данные: -1")
                return
            product_coefficient = float(product_result[0])
            
            cursor.execute("SELECT loss_percentage FROM materials_type WHERE id_material_type = %s", (data["material_type_id"],))
            material_result = cursor.fetchone()
            if not material_result:
                cursor.close()
                conn.close()
                messagebox.showerror("Ошибка", "Некорректные данные: -1")
                return
            material_loss_percent = float(material_result[0])
            
            cursor.close()
            conn.close()
            
            material_per_unit = data["param1"] * data["param2"] * product_coefficient
            
            effective_material_quantity = data["material_quantity"] * (1 - material_loss_percent / 100)
            
            product_quantity = math.floor(effective_material_quantity / material_per_unit)
            
            messagebox.showinfo("Итого", "Количество сырья: " + str(product_quantity))

        except db.mysql.connector.Error:
            messagebox.showerror("Ошибка", "Некорректные данные: -1")
            return


class MainScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Материалы на складе — Образ Плюс")
        self.geometry("780x600")
        self.configure(bg=BG_MAIN)

        try:
            self.iconbitmap("resources/Образ плюс.ico")
            logo = tk.PhotoImage(file="resources/Образ плюс.png")
            logo = logo.subsample(max(1, logo.width() // 100))
            tk.Label(self, image=logo, bg=BG_MAIN).pack()
            self.logo = logo
        except:
            pass

        self.page_container = tk.Frame(self, bg=BG_MAIN)
        self.page_container.pack(fill="both", expand=True)

        self.page_list = tk.Frame(self.page_container, bg=BG_MAIN)
        self.page_list.grid(row=0, column=0, sticky="nsew")

        self.page_form = None
        self.page_product_list = None

        tk.Button(self.page_list, text="Добавить материал", bg=ACCENT, fg='white',
                  command=lambda: self.show_form()).pack(pady=5)
        tk.Button(self.page_list, text="Расчет продукции", bg=ACCENT, fg='white',
                  command=lambda: self.show_form_calculation()).pack(pady=5)
        
        self.scroll_frame = tk.Frame(self.page_list, bg=BG_MAIN)
        self.scroll_frame.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(self.scroll_frame, bg=BG_MAIN)
        self.canvas.config(height=350, width=750) 
        self.scrollbar = tk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.card_container = tk.Frame(self.canvas, bg=BG_MAIN)

        self.card_container.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        def resize_canvas(event):
            self.canvas.itemconfig("card_window", width=event.width)
        self.canvas.create_window((0, 0), window=self.card_container, anchor="nw", tags="card_window")
        self.canvas.bind("<Configure>", resize_canvas)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * e.delta / 120), "units"))

        self.load_cards()
        self.show_list()

    def show_list(self):
        self.title("Материалы на складе — Образ Плюс")
        self.load_cards() 
        self.page_list.tkraise()

    def show_form(self, material=None):
        if self.page_form:
            self.page_form.destroy()
        self.page_form = MaterialForm(self.page_container, self.show_list, material)

        if material == None:
            self.title("Добавление материала — Образ Плюс")   
        else:
            self.title("Редактирование материала — Образ Плюс")

        self.page_form.grid(row=0, column=0, sticky="nsew")
        self.page_form.tkraise()
        
    def show_product_list(self, material):
        if self.page_product_list:
            self.page_product_list.destroy()
        self.page_product_list = ProductListForm(self.page_container, self.show_list, material)
        self.title("Продукция для материала — Образ Плюс")
        self.page_product_list.grid(row=0, column=0, sticky="nsew")
        self.page_product_list.tkraise()

    def load_cards(self):
        for w in self.card_container.winfo_children():
            w.destroy()

        for mat in db.fetch_all_materials():
            card = tk.Frame(self.card_container, bg=BG_MAIN, bd=2, relief='groove', padx=5, pady=5)
            card.pack(fill='x', expand=True, padx=10, pady=5)

            row1 = tk.Frame(card, bg=BG_MAIN)
            row1.pack(fill='x')
            tk.Label(row1, text=f"{mat['type']} | {mat['name']}",
                     font=(FONT_MAIN[0], 12, 'bold'), bg=BG_MAIN).pack(side='left', fill='x', expand=False)
            tk.Label(row1, text=f"Требуется: {mat['required']:.2f}", font=FONT_MAIN, bg=BG_MAIN).pack(side='right', padx=10)

            row2 = tk.Frame(card, bg=BG_MAIN)
            row2.pack(fill='x', pady=2)
            tk.Label(row2, text=f"Минимальный остаток: {mat['min_stock']:.2f}",
                     font=FONT_SMALL, bg=BG_MAIN).pack(side='left')

            row3 = tk.Frame(card, bg=BG_MAIN)
            row3.pack(fill='x', pady=2)
            tk.Label(row3, text=f"На складе: {mat['stock']:.2f} {mat['unit']}",
                     font=FONT_SMALL, bg=BG_MAIN).pack(side='left')

            row4 = tk.Frame(card, bg=BG_MAIN)
            row4.pack(fill='x', pady=2)
            tk.Label(row4, text=f"Цена: {mat['price']:.2f} руб. | упак.: {mat['pack_qty']:.2f} {mat['unit']}",
                     font=FONT_SMALL, bg=BG_MAIN).pack(side='left')
            tk.Button(row4, text="Продукция", bg=BG_SECOND, fg="black",
                      command=lambda m=mat: self.show_product_list(m)).pack(side='right', padx=5)
                    
            card.bind("<Button-1>", lambda e, m=mat: self.show_form(m))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, m=mat: self.show_form(m))

    def show_form_calculation(self):
        if self.page_form:
            self.page_form.destroy()
        self.page_form = material_cacl_form.MaterialCalculationForm(self.page_container, self.show_list)
        self.title("Расчет продукции — Образ Плюс")
        self.page_form.grid(row=0, column=0, sticky="nsew")
        self.page_form.tkraise()


if __name__ == "__main__":
    MainScreen().mainloop()
