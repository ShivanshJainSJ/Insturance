import tkinter as tk
from tkinter import messagebox
import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
import requests
import json

# Set your Gemini API endpoint and API key
GEMINI_API_URL = "https://api.gemini.com/v1/graph"  # Replace with the correct endpoint
API_KEY = "AIzaSyCg9twMXaG83a8D6Ua3Tbbh53vOq_dIiF4"  # Replace with your actual Gemini API key

def calculate():
    expression = entry.get()
    try:
        result = eval(expression)
        result_label.config(text=f"Result: {result}")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid expression: {e}")

def generate_graph():
    equation = entry.get()
    try:
        # Prepare the request to the Gemini API
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            "equation": equation
        }
        
        # Send the request to the Gemini API
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            graph_data = response.json()
            x = np.linspace(-10, 10, 400)
            y = eval(equation)  # Assuming the equation is valid and can be evaluated
            
            # Create a Plotly graph
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=equation))
            fig.update_layout(title=f'Graph of {equation}',
                              xaxis_title='x',
                              yaxis_title='y',
                              showlegend=True)
            
            # Save the graph as an HTML file and open it in the browser
            pyo.plot(fig, filename='graph.html', auto_open=True)
        else:
            messagebox.showerror("Error", f"Failed to generate graph: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid equation: {e}")

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