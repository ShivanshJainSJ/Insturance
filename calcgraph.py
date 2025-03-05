import tkinter as tk
from tkinter import messagebox
import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
import openai
import os

# Set your OpenAI API key
openai.api_key = ''  # Replace with your actual OpenAI API key

def calculate():
    expression = entry.get()
    try:
        result = eval(expression)
        result_label.config(text=f"Result: {result}")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid expression: {e}")

def generate_graph():
    user_input = entry.get()
    try:
        # Use OpenAI API to generate graphing code
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Generate Python code to plot the following function: {user_input}"}
            ]
        )
        
        # Extract the generated code from the response
        generated_code = response['choices'][0]['message']['content']
        
        # Execute the generated code
        local_namespace = {}
        exec(generated_code, {"np": np, "go": go, "plt": plt}, local_namespace)
        
        # Create a Plotly graph
        fig = local_namespace['fig']
        pyo.plot(fig, filename='graph.html', auto_open=True)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate graph: {e}")

app = tk.Tk()
app.title("Calculator and Graph Bot")

entry = tk.Entry(app, width=40)
entry.pack(pady=20)

calc_button = tk.Button(app, text="Calculate", command=calculate)
calc_button.pack(pady=10)

result_label = tk.Label(app, text="Result: ")
result_label.pack(pady=10)

graph_button = tk.Button(app, text="Generate Graph", command=generate_graph)
graph_button.pack(pady=10)

app.mainloop()