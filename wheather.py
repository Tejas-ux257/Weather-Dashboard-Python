import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json

class WeatherDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title(" Weather Dashboard ")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # API Configuration
        self.api_key = "YOUR_API_KEY"  # Get free key from openweathermap.org
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        
        self.weather_data = None
        self.forecast_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg="#FF5722", height=80)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            title_frame, 
            text="🌤  WEATHER DASHBOARD",
            font=("Arial", 24, "bold"),
            bg="#FF5722",
            fg="white"
        )
        title_label.pack(pady=20)
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(pady=10)
        
        tk.Label(
            input_frame, 
            text="Enter City:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=0, column=0, padx=5)
        
        self.city_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.city_entry.grid(row=0, column=1, padx=5)
        self.city_entry.insert(0, "city name")
        
        self.fetch_btn = tk.Button(
            input_frame,
            text="Fetch Weather Data",
            command=self.fetch_weather,
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            cursor="hand2",
            padx=20,
            pady=5
        )
        self.fetch_btn.grid(row=0, column=2, padx=5)  
      
        self.info_frame = tk.LabelFrame(
            self.root,
            text="Current Weather Information",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333"
        )
        self.info_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=False)
       
        self.info_labels = {}
        info_fields = [
            "City", "Temperature", "Feels Like", "Humidity",
            "Pressure", "Wind Speed", "Weather", "Description"
        ]
        
        for i, field in enumerate(info_fields):
            row = i // 4
            col = (i % 4) * 2
            
            tk.Label(
                self.info_frame,
                text=f"{field}:",
                font=("Arial", 11, "bold"),
                bg="white",
                anchor="w"
            ).grid(row=row, column=col, sticky="w", padx=10, pady=5)
            
            self.info_labels[field] = tk.Label(
                self.info_frame,
                text="--",
                font=("Arial", 11),
                bg="white",
                fg="#2196F3",
                anchor="w"
            )
            self.info_labels[field].grid(row=row, column=col+1, sticky="w", padx=10, pady=5)
        
  
        viz_frame = tk.LabelFrame(
            self.root,
            text="Data Visualizations",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333"
        )
        viz_frame.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)
        
        self.fig = Figure(figsize=(12, 5), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
  
        self.status_bar = tk.Label(
            self.root,
            text="Ready - Enter a city and click 'Fetch Weather Data'",
            font=("Arial", 10),
            bg="#333",
            fg="white",
            anchor="w"
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def fetch_weather(self):
        city = self.city_entry.get().strip()
        
        if not city:
            messagebox.showerror("Error", "Please enter a city name!")
            return
        
        self.status_bar.config(text=f"Fetching weather data for {city}...")
        self.root.update()
        
        try:
            
            current_params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            current_response = requests.get(self.base_url, params=current_params)
            
            if current_response.status_code == 401:
                messagebox.showerror(
                    "API Key Error",
                    "Invalid API Key!\n\nPlease:\n1. Get a free API key from openweathermap.org\n2. Replace 'YOUR_API_KEY' in the code\n3. Try again"
                )
                self.status_bar.config(text="Error: Invalid API Key")
                return
            
            if current_response.status_code == 404:
                messagebox.showerror("Error", f"City '{city}' not found!")
                self.status_bar.config(text=f"Error: City not found")
                return
                
            current_response.raise_for_status()
            self.weather_data = current_response.json()
            
      
            forecast_params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            forecast_response = requests.get(self.forecast_url, params=forecast_params)
            forecast_response.raise_for_status()
            self.forecast_data = forecast_response.json()
            
       
            self.update_info()
            self.create_visualizations()
            
            self.status_bar.config(text=f"Successfully fetched data for {city}")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network Error", f"Failed to fetch data:\n{str(e)}")
            self.status_bar.config(text="Error: Network request failed")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status_bar.config(text="Error occurred")
    
    def update_info(self):
        """Update current weather information"""
        data = self.weather_data
        
        self.info_labels["City"].config(
            text=f"{data['name']}, {data['sys']['country']}"
        )
        self.info_labels["Temperature"].config(
            text=f"{data['main']['temp']:.1f}°C"
        )
        self.info_labels["Feels Like"].config(
            text=f"{data['main']['feels_like']:.1f}°C"
        )
        self.info_labels["Humidity"].config(
            text=f"{data['main']['humidity']}%"
        )
        self.info_labels["Pressure"].config(
            text=f"{data['main']['pressure']} hPa"
        )
        self.info_labels["Wind Speed"].config(
            text=f"{data['wind']['speed']} m/s"
        )
        self.info_labels["Weather"].config(
            text=data['weather'][0]['main']
        )
        self.info_labels["Description"].config(
            text=data['weather'][0]['description'].title()
        )
    
    def create_visualizations(self):
        """Create weather data visualizations"""
        self.fig.clear()
        
        forecast_list = self.forecast_data['list'][:8]  # Next 24 hours
        
        temps = [item['main']['temp'] for item in forecast_list]
        feels_like = [item['main']['feels_like'] for item in forecast_list]
        humidity = [item['main']['humidity'] for item in forecast_list]
        times = [item['dt_txt'].split()[1][:5] for item in forecast_list]
        
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
      
        ax1 = self.fig.add_subplot(gs[0, :])
        ax1.plot(times, temps, marker='o', linewidth=2, 
                markersize=8, color='#FF5722', label='Temperature')
        ax1.plot(times, feels_like, marker='s', linewidth=2, 
                markersize=6, color='#2196F3', label='Feels Like', linestyle='--')
        ax1.set_xlabel('Time', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Temperature (°C)', fontsize=10, fontweight='bold')
        ax1.set_title('24-Hour Temperature Forecast', fontsize=12, fontweight='bold', pad=10)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
      
        ax2 = self.fig.add_subplot(gs[1, 0])
        bars = ax2.bar(times, humidity, color='#4CAF50', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Time', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Humidity (%)', fontsize=10, fontweight='bold')
        ax2.set_title('Humidity Levels', fontsize=12, fontweight='bold', pad=10)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
       
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}%', ha='center', va='bottom', fontsize=8)
        
       
        ax3 = self.fig.add_subplot(gs[1, 1])
        
        current = self.weather_data['main']
        stats = {
            'Temperature': current['temp'],
            'Feels Like': current['feels_like'],
            'Min Temp': current['temp_min'],
            'Max Temp': current['temp_max']
        }
        
        colors = ['#FF5722', '#2196F3', '#4CAF50', '#FFC107']
        wedges, texts, autotexts = ax3.pie(
            stats.values(),
            labels=stats.keys(),
            autopct='%1.1f°C',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 9, 'fontweight': 'bold'}
        )
        
        ax3.set_title('Temperature Distribution', fontsize=12, fontweight='bold', pad=10)
        
        self.canvas.draw()
    
    def save_data(self):
        """Save weather data to JSON file"""
        if self.weather_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weather_data_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump({
                    'current': self.weather_data,
                    'forecast': self.forecast_data
                }, f, indent=4)
            
            messagebox.showinfo("Success", f"Data saved to {filename}")

def main():
    root = tk.Tk()
    app = WeatherDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
