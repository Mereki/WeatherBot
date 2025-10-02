import os
import discord
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)


def get_weather_data(city: str, state: str = None):
    """
    Gets comprehensive weather data using a 2-step API call process.
    1. Geocoding API: Converts city/state to latitude/longitude.
    2. One Call API: Gets current, hourly, and daily forecasts for the coordinates.
    """

    # Geocoding API call
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    location_query = city
    if state:
        location_query += f",{state},US"

    geo_params = {"q": location_query, "limit": 1, "appid": WEATHER_API_KEY}
    geo_response = requests.get(geo_url, params=geo_params)

    if geo_response.status_code != 200 or not geo_response.json():
        return None  # Location not found

    geo_data = geo_response.json()[0]
    lat, lon = geo_data['lat'], geo_data['lon']

    # One Call API call
    one_call_url = "https://api.openweathermap.org/data/3.0/onecall"
    one_call_params = {
        "lat": lat,
        "lon": lon,
        "appid": WEATHER_API_KEY,
        "units": "imperial",
        "exclude": "minutely,daily,alerts"  # We only need current and hourly
    }
    weather_response = requests.get(one_call_url, params=one_call_params)

    if weather_response.status_code == 200:
        return weather_response.json()
    else:
        return None


@bot.event
async def on_ready():
    await tree.sync()
    print(f'✅ Logged in as {bot.user}')
    print(f'✨ Bot is ready and slash commands are synced!')

# Overview cmd
@tree.command(name="overview", description="Get a general weather overview for a city (and optional state).")
async def overview(interaction: discord.Interaction, city: str, state: str = None):
    weather_data = get_weather_data(city, state)

    if weather_data:
        current = weather_data['current']
        weather_desc = current['weather'][0]

        location_name = city.title()
        if state:
            location_name += f", {state.upper()}"

        embed = discord.Embed(
            title=f"Weather Overview for {location_name}",
            description=f"It's currently **{weather_desc['description']}**.",
            color=discord.Color.blue()
        )
        embed.add_field(name="🌡️ Temperature", value=f"{current['temp']}°F", inline=True)
        embed.add_field(name="🤔 Feels Like", value=f"{current['feels_like']}°F", inline=True)
        embed.add_field(name="💧 Humidity", value=f"{current['humidity']}%", inline=True)
        embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{weather_desc['icon']}@2x.png")
        embed.set_footer(text="Data provided by OpenWeatherMap")

        await interaction.response.send_message(embed=embed)
    else:
        error_location = city
        if state: error_location += f", {state}"
        await interaction.response.send_message(f"Could not find weather data for '{error_location}'.", ephemeral=True)


# Rain cmd
@tree.command(name="rain", description="Shows the hourly chance of rain for the next 12 hours.")
async def rain(interaction: discord.Interaction, city: str, state: str = None):
    weather_data = get_weather_data(city, state)

    if weather_data:
        location_name = city.title()
        if state: location_name += f", {state.upper()}"

        embed = discord.Embed(
            title=f"🌧️ Hourly Rain Forecast for {location_name}",
            color=discord.Color.dark_blue()
        )

        hourly_forecasts = weather_data['hourly'][:12]
        timezone_offset = weather_data['timezone_offset']

        forecast_lines = []
        for hour in hourly_forecasts:
            chance_of_rain = hour['pop']
            if chance_of_rain > 0.1:
                dt_object = datetime.fromtimestamp(hour['dt'], tz=timezone.utc) + timedelta(seconds=timezone_offset)
                time_str = dt_object.strftime('%I:%M %p')

                rain_percentage = int(chance_of_rain * 100)
                forecast_lines.append(f"**{time_str.lstrip('0')}**: {rain_percentage}% chance of rain")
        if forecast_lines:
            embed.description = "\n".join(forecast_lines)
        else:
            embed.description = "No significant chance of rain in the next 12 hours. ☀️"
        await interaction.response.send_message(embed=embed)
    else:
        error_location = city
        if state: error_location += f", {state}"
        await interaction.response.send_message(f"Could not find weather data for '{error_location}'.", ephemeral=True)


# Wind cmd
@tree.command(name="wind", description="Check the wind conditions for a city (and optional state).")
async def wind(interaction: discord.Interaction, city: str, state: str = None):
    weather_data = get_weather_data(city, state)
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    if weather_data:
        wind_speed = weather_data['current']['wind_speed']
        wind_deg = weather_data['current']['wind_deg']
        index = int((wind_deg + 22.5) / 45) % 8

        location_name = city.title()
        if state: location_name += f", {state.upper()}"

        embed = discord.Embed(
            title=f"💨 Wind Conditions for {location_name}",
            color=discord.Color.light_grey()
        )

        embed.add_field(name="Speed", value=f"{wind_speed} mph", inline=True)
        embed.add_field(name="Direction", value=f"{wind_deg}°, {directions[index]}", inline=True)

        await interaction.response.send_message(embed=embed)
    else:
        error_location = city
        if state: error_location += f", {state}"
        await interaction.response.send_message(f"Could not find weather data for '{error_location}'.", ephemeral=True)

bot.run(DISCORD_TOKEN)