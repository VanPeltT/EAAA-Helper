import requests
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from io import BytesIO
from bs4 import BeautifulSoup

counter = 0

def get_weather_data_by_lat_lon(api_key, latitude, longitude):
    """Fetches weather data from WeatherAPI using latitude and longitude."""
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={latitude},{longitude}&days=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def update_weather(api_key, latitude, longitude, label):
    """Fetch and update weather information on the GUI."""
    global counter
    weather_data = get_weather_data_by_lat_lon(api_key, latitude, longitude)
    counter += 1
    print("Number of calls:", counter)
    if weather_data:
        current_time = datetime.now()
        date_str = current_time.strftime("%m/%d/%Y")
        time_str = current_time.strftime("\n%I:%M %p")
        current_temp_f = weather_data['current']['temp_f']
        feels_like_f = weather_data['current']['feelslike_f']
        conditions = (
            f"Location: {weather_data['location']['name']}, {weather_data['location']['region']}\n"
            f"{date_str} {time_str}\n"
            f"Temperature: {current_temp_f} °F\n"
            f"Humidity: {weather_data['current']['humidity']}%\n"
            f"Feels Like: {feels_like_f} °F\n"
            f"Cloud Cover: {weather_data['current']['condition']['text']}\n"
            f"Wind: {weather_data['current']['wind_mph']} mph\n"
            f"Wind Gust: {weather_data['current']['gust_mph']} mph\n"
            f"Wind Direction: {weather_data['current']['wind_dir']}\n\n"
        )
        
        forecast = weather_data['forecast']['forecastday'][0]
        forecast_info = (
            f"Forecast for Today:\n"
            f"High Temperature: {forecast['day']['maxtemp_f']} °F\n"
            f"Minimum Temperature: {forecast['day']['mintemp_f']} °F\n"
            f"Chance of Precipitation: {forecast['day']['daily_chance_of_rain']}%\n"
            f"Total Precipitation: {forecast['day']['totalprecip_in']} in\n\n"
        )
        
        astro_info = (
            f"Astronomy Forecast for Today:\n"
            f"Sunrise: {forecast['astro']['sunrise']}\n"
            f"Sunset: {forecast['astro']['sunset']}\n"
            f"Moon Phase: {forecast['astro']['moon_phase']}\n"
            f"Moon Rise: {forecast['astro']['moonrise']}\n"
            f"Moon Set: {forecast['astro']['moonset']}\n"
        )

        label.config(text=conditions + forecast_info + astro_info)
    
    # Refresh the weather information every 5 minutes
    label.after(300000, update_weather, api_key, latitude, longitude, label)

def retrieve_weather_data():
    api_key = "d2db2aadf20b489fbe4112953242008"
    latitude = 30.5925727
    longitude = -87.0916525
    
    # Create the main window
    root = tk.Tk()
    root.title("Weather Information")
    root.geometry("285x550")
    root.configure(bg="#282c34")

    # Create a label to display the weather information
    weather_label = ttk.Label(root, text="", justify="center", font=("Helvetica", 12), background="#f0f0f0", borderwidth=2, relief="solid", padding=10)
    weather_label.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Create a button for manual refresh
    refresh_button = ttk.Button(root, text="Refresh", command=lambda: update_weather(api_key, latitude, longitude, weather_label))
    refresh_button.pack(pady=10)

    # Start the weather update loop
    update_weather(api_key, latitude, longitude, weather_label)

    # Run the GUI loop
    root.mainloop()
    
# Helper function to center windows
def center_window(window, width, height):
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate position x, y
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    # Set the window position
    window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

# Function to show downloaded image
def show_converted_image():
    # URL of the image
    image_url = "https://www.cleardarksky.com/c/PnsclFLcsk.gif"

    # Define headers to mimic a browser request
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    # Download the image with headers
    response = requests.get(image_url, headers=headers)

    # Check the status code and content type
    if response.status_code == 200 and 'image' in response.headers['Content-Type']:
        # Open the image
        image_data = Image.open(BytesIO(response.content))

        # Convert the image to RGB if it's not already (required for JPEG format)
        if image_data.mode != 'RGB':
            image_data = image_data.convert('RGB')

        # Create a Tkinter window
        image_window = tk.Toplevel(root)
        image_window.title("Pensacola Clear Sky Chart")

        # Convert the image to a format Tkinter can use
        tk_image = ImageTk.PhotoImage(image_data)

        # Create a label to display the image
        label = tk.Label(image_window, image=tk_image)
        label.pack()

        # Keep a reference to the image to prevent it from being garbage collected
        label.image = tk_image

        # Center the image window
        center_window(image_window, image_data.width, image_data.height + 50)

        # Function to save the image
        def save_image():
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if file_path:
                image_data.save(file_path, format='JPEG')

        # Add the Save Image button
        save_btn = ttk.Button(image_window, text="Save Image", command=save_image)
        save_btn.pack(pady=10)

    else:
        messagebox.showerror("Error", f"Failed to download image. Status code: {response.status_code}, Content-Type: {response.headers['Content-Type']}")

# Function to convert 24-hour time format to 12-hour AM/PM format
def convert_to_ampm(time_str):
    try:
        time_str = time_str.strip()[:-4].strip()
        return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
    except ValueError:
        return "Invalid Time"

# Function to format and display seasons data
def format_seasons_data(events):
    formatted_events = []
    for event in events:
        event_time = f"{event['year']}-{event['month']:02d}-{event['day']:02d}"
        try:
            formatted_time = datetime.strptime(event_time, '%Y-%m-%d').strftime('%B %d, %Y')
            formatted_events.append(f" - {event['phenom']}: {formatted_time}")
        except ValueError:
            formatted_events.append(f" - {event['phenom']}: Invalid Date")
    return formatted_events

# Function to display and save the solar image
def display_solar_image(url, title):
    try:
        response = requests.get(url)
        response.raise_for_status()

        image_data = None
        
        if url.endswith(".html"):
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and 'src' in img_tag.attrs:
                image_url = img_tag['src']
                if not image_url.startswith('http'):
                    image_url = f"https://soho.nascom.nasa.gov{image_url}"
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                image_data = BytesIO(image_response.content)
            else:
                raise ValueError("Image URL not found in HTML")
        else:
            image_data = BytesIO(response.content)

        img = Image.open(image_data)

        max_size = 800
        width, height = img.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            new_size = (int(width * ratio), int(height * ratio))
            img_resized = img.resize(new_size, Image.ANTIALIAS)
        else:
            img_resized = img

        img_width, img_height = img_resized.size
        image_window = tk.Toplevel(root)
        image_window.title(title)
        center_window(image_window, img_width, img_height + 50)  # Center the image window

        img_tk = ImageTk.PhotoImage(img_resized)
        image_label = tk.Label(image_window, image=img_tk)
        image_label.pack()

        def save_image():
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if file_path:
                img_resized.save(file_path)

        save_btn = ttk.Button(image_window, text="Save Image", command=save_image)
        save_btn.pack(pady=10)

        image_label.image = img_tk

    except requests.RequestException as e:
        messagebox.showerror("Error", f"Error retrieving the solar image: {e}")
    except ValueError as e:
        messagebox.showerror("Error", f"Error processing data: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")

def retrieve_data():
    try:
        today = datetime.now().strftime('%Y-%m-%d')

        astro_url = f"https://aa.usno.navy.mil/api/rstt/oneday?date={today}&coords=30.5925727,-87.0916525&tz=-6&dst=true"
        astro_response = requests.get(astro_url)
        astro_response.raise_for_status()
        astro_data = astro_response.json()

        properties = astro_data.get("properties", {}).get("data", {})

        date = f"{properties.get('day_of_week', '')}, {properties.get('month', '')}/{properties.get('day', '')}/{properties.get('year', '')}"
        closest_phase = properties.get("closestphase", {})
        moon_phase = closest_phase.get("phase", "N/A")
        moon_phase_date = f"{closest_phase.get('month', '')}/{closest_phase.get('day', '')}/{closest_phase.get('year', '')}"
        moon_phase_time = closest_phase.get("time", "N/A")

        moon_data = {item['phen']: convert_to_ampm(item['time']) for item in properties.get("moondata", [])}
        moon_rise = moon_data.get("Rise", "No Moon Rise")
        moon_set = moon_data.get("Set", "No Moon Set")
        moon_upper_transit = moon_data.get("Upper Transit", "N/A")

        sun_data = {item['phen']: convert_to_ampm(item['time']) for item in properties.get("sundata", [])}
        sun_rise = sun_data.get("Rise", "N/A")
        sun_set = sun_data.get("Set", "N/A")
        sun_upper_transit = sun_data.get("Upper Transit", "N/A")
        civil_twilight_end = sun_data.get("End Civil Twilight", "N/A")

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Date: {date}\n")
        result_text.insert(tk.END, f"Closest Phase of the Moon: {moon_phase} on {moon_phase_date} at {convert_to_ampm(moon_phase_time)}\n")
        result_text.insert(tk.END, "Moon Data:\n")
        result_text.insert(tk.END, f"  - Rise Time: {moon_rise}\n")
        result_text.insert(tk.END, f"  - Set Time: {moon_set}\n")
        result_text.insert(tk.END, f"  - Upper Transit Time: {moon_upper_transit}\n")
        result_text.insert(tk.END, "Sun Data:\n")
        result_text.insert(tk.END, f"  - Rise Time: {sun_rise}\n")
        result_text.insert(tk.END, f"  - Set Time: {sun_set}\n")
        result_text.insert(tk.END, f"  - Upper Transit Time: {sun_upper_transit}\n")
        result_text.insert(tk.END, f"  - End of Civil Twilight: {civil_twilight_end}\n")

    except requests.RequestException as e:
        messagebox.showerror("Error", f"Error retrieving astronomical data: {e}")
    except ValueError as e:
        messagebox.showerror("Error", f"Error processing data: {e}")

def retrieve_eclipse_data():
    try:
        # Get the current year
        current_year = datetime.now().year

        eclipse_url = f"https://aa.usno.navy.mil/api/eclipses/solar/year?year={current_year}&coords=30.5925727,-87.0916525&height=15"
        eclipse_response = requests.get(eclipse_url)
        eclipse_response.raise_for_status()  # Check for HTTP request errors
        eclipse_data = eclipse_response.json()

        # Display the Solar Eclipse Data
        result_text.insert(tk.END, "\nSolar Eclipse Data:\n")
        for eclipse in eclipse_data['eclipses_in_year']:
            event_date = f"{eclipse['year']}-{eclipse['month']:02d}-{eclipse['day']:02d}"
            formatted_date = datetime.strptime(event_date, '%Y-%m-%d').strftime('%B %d, %Y')
            result_text.insert(tk.END, f"  - {eclipse['event']}: {formatted_date}\n")

    except requests.RequestException as e:
        messagebox.showerror("Error", f"Error retrieving solar eclipse data: {e}")
    except ValueError as e:
        messagebox.showerror("Error", f"Error processing data: {e}")

def retrieve_solar_data():
    try:
        # Get the current year
        current_year = datetime.now().year

        seasons_url = f"https://aa.usno.navy.mil/api/seasons?year={current_year}"
        seasons_response = requests.get(seasons_url)
        seasons_response.raise_for_status()  # Check for HTTP request errors
        seasons_data = seasons_response.json()

        # Display the Seasons Data
        result_text.insert(tk.END, "\nSolar Data:\n")
        formatted_events = format_seasons_data(seasons_data['data'])
        for event in formatted_events:
            result_text.insert(tk.END, f"{event}\n")

    except requests.RequestException as e:
        messagebox.showerror("Error", f"Error retrieving seasons data: {e}")
    except ValueError as e:
        messagebox.showerror("Error", f"Error processing data: {e}")

# Create the main window
root = tk.Tk()
root.title("Astronomical Data Viewer by TVP and Retrieved from https://aa.usno.navy.mil/data/api")

# Set the window size (width x height)
main_window_width = 685
main_window_height = 800
root.geometry(f"{main_window_width}x{main_window_height}")

# Center the main window
center_window(root, main_window_width, main_window_height)

# Create and configure the GUI layout
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# GUI Elements
ttk.Label(frame, text="Escambia Amateur Astronomer's Association", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

result_text = tk.Text(frame, width=80, height=30, wrap="word")
result_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

retrieve_btn = ttk.Button(frame, text="Retrieve Astronomical Data", command=retrieve_data)
retrieve_btn.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

eclipse_btn = ttk.Button(frame, text="Retrieve Solar Eclipse Data", command=retrieve_eclipse_data)
eclipse_btn.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

seasons_btn = ttk.Button(frame, text="Retrieve Solar Data", command=retrieve_solar_data)
seasons_btn.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

seasons_btn = ttk.Button(frame, text="Retrieve Weather Data", command=retrieve_weather_data)
seasons_btn.grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)

hmi_image_btn = ttk.Button(frame, text="Display SDO/HMI Continuum Image", command=lambda: display_solar_image("https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg", "SOHO HMI Solar Image - the continuum near the Ni I 6768 Angstrom line"))
hmi_image_btn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

eit_image_btn_171 = ttk.Button(frame, text="Display SOHO EIT 171 Latest Image", command=lambda: display_solar_image("https://soho.nascom.nasa.gov/data/realtime/eit_171/1024/latest.jpg", "SOHO EIT 171 Solar Image - bright material is at 1 million degrees Kelvin"))
eit_image_btn_171.grid(row=4, column=1, padx=5, pady=5, sticky=tk.E)

eit_image_btn_195 = ttk.Button(frame, text="Display SOHO EIT 195 Latest Image", command=lambda: display_solar_image("https://soho.nascom.nasa.gov/data/realtime/eit_195/1024/latest.jpg", "SOHO EIT 195 Solar Image - bright material is at 1.5 million degrees Kelvin"))
eit_image_btn_195.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

eit_image_btn_284 = ttk.Button(frame, text="Display SOHO EIT 284 Latest Image", command=lambda: display_solar_image("https://soho.nascom.nasa.gov/data/realtime/eit_284/1024/latest.jpg", "SOHO EIT 284 Solar Image - bright material is at 2 million degrees Kelvin"))
eit_image_btn_284.grid(row=5, column=1, padx=5, pady=5, sticky=tk.E)

eit_image_btn_304 = ttk.Button(frame, text="Display SOHO EIT 304 Latest Image", command=lambda: display_solar_image("https://soho.nascom.nasa.gov/data/realtime/eit_304/1024/latest.jpg", "SOHO EIT 304 Solar Image - bright material is at 60,000 to 80,000 degrees Kelvin"))
eit_image_btn_304.grid(row=6, column=0, columnspan=2, pady=10)

image_btn = ttk.Button(frame, text="Display the Pensacola Clear Sky Chart", command=show_converted_image)
image_btn.grid(row=7, column=0, columnspan=2, pady=10)

root.mainloop()

