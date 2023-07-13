import tkinter as tk

def on_positive():
    print("Comentario positivo")

def on_neutral():
    print("Comentario neutral")

def on_negative():
    print("Comentario negativo")

root = tk.Tk()
root.title("Review Comments")

text_block = tk.Text(root)
text_block.pack(fill=tk.BOTH, expand=True)

initial_text = "Este es un ejemplo de texto."
text_block.insert(tk.END, initial_text)
text_block.configure(state="disabled")

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

positive_button = tk.Button(button_frame, text="Positivo", bg="green", command=on_positive)
positive_button.pack(side=tk.LEFT, padx=5)

neutral_button = tk.Button(button_frame, text="Neutral", bg="gray", command=on_neutral)
neutral_button.pack(side=tk.LEFT, padx=5)

negative_button = tk.Button(button_frame, text="Negativo", bg="red", command=on_negative)
negative_button.pack(side=tk.LEFT, padx=5)

root.mainloop()