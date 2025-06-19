
import tkinter as tk
from tkinter import ttk, messagebox
import db
from main import BG_MAIN, ACCENT,FONT_MAIN


class MaterialForm(tk.Frame):
    def __init__(self, parent, return_callback, material=None):
        super().__init__(parent, bg=BG_MAIN)
        self.return_callback = return_callback
        self.material = material
        self.types = db.fetch_material_types()

        if material == None:
            tk.Label(self, text="Добавление материала", font=("Constantia", 14), bg=BG_MAIN).pack(pady=10)
        else:
            tk.Label(self, text="Редактирование материала", font=("Constantia", 14), bg=BG_MAIN).pack(pady=10)

        form = tk.Frame(self, bg=BG_MAIN)
        form.pack(pady=10)
        self.var_type = tk.StringVar()
        self.vars = {}
        fields = [
            ("Тип материала", self.var_type),
            ("Наименование", tk.StringVar()),
            ("Цена", tk.StringVar()),
            ("Ед. изм.", tk.StringVar()),
            ("Кол-во в упак.", tk.StringVar()),
            ("Остаток", tk.StringVar()),
            ("Мин. остаток", tk.StringVar())
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(form, text=label + ":", font=FONT_MAIN, bg=BG_MAIN).grid(row=i, column=0, sticky="e", pady=2)
            if label == "Тип материала":
                combo = ttk.Combobox(form, textvariable=var, values=list(self.types.keys()), state='readonly', width=30)
                combo.grid(row=i, column=1, padx=5)
                combo.set(list(self.types.keys())[0])
            else:
                entry = tk.Entry(form, textvariable=var, width=33)
                entry.grid(row=i, column=1, padx=5)
                self.vars[label] = var

        if material:
            self.var_type.set(material["type"])
            self.vars["Наименование"].set(material["name"])
            self.vars["Цена"].set(f"{material['price']:.2f}")
            self.vars["Ед. изм."].set(material["unit"])
            self.vars["Кол-во в упак."].set(f"{material['pack_qty']:.2f}")
            self.vars["Остаток"].set(f"{material['stock']:.2f}")
            self.vars["Мин. остаток"].set(f"{material['min_stock']:.2f}")

        btns = tk.Frame(self, bg=BG_MAIN)
        btns.pack(pady=10)
        tk.Button(btns, text="Сохранить", bg=ACCENT, fg="white", command=self.save).pack(side="left", padx=5)
        tk.Button(btns, text="Назад", command=self.return_callback).pack(side="left", padx=5)

    def save(self):
        try:
            data = {
                "id_material_type": self.types[self.var_type.get()],
                "name": self.vars["Наименование"].get(),
                "price": float(self.vars["Цена"].get()),
                "unit": self.vars["Ед. изм."].get(),
                "pack_qty": float(self.vars["Кол-во в упак."].get()),
                "stock": float(self.vars["Остаток"].get()),
                "min_stock": float(self.vars["Мин. остаток"].get())
            }
            # валидируем данные
            if data["price"] < 0 or data["min_stock"] < 0:
                raise ValueError("Цена и минимальный остаток не могут быть отрицательными.")
            if data["name"] == "":
                raise ValueError("У материала не может быть пустого названия.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return

        conn = db.get_db_connection()
        cur = conn.cursor()
        try:
            if self.material:
                cur.execute("""
                    UPDATE materials SET name=%s, id_material_type=%s, unit_price=%s,
                        in_stock=%s, min_stock=%s, pack_size=%s, unit=%s
                    WHERE id_material=%s
                """, (
                    data["name"], data["id_material_type"], data["price"],
                    data["stock"], data["min_stock"], data["pack_qty"],
                    data["unit"], self.material["id"]
                ))
            else:
                cur.execute("""
                    INSERT INTO materials (name, id_material_type, unit_price,
                        in_stock, min_stock, pack_size, unit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data["name"], data["id_material_type"], data["price"],
                    data["stock"], data["min_stock"], data["pack_qty"],
                    data["unit"]
                ))
            conn.commit()
        # обрабатываем любую ошибку; выводим    
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))
            return
        finally:
            cur.close()
            conn.close()

        messagebox.showinfo("Успех", "Материал сохранён.")
        self.return_callback()
