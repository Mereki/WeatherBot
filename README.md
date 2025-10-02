# WeatherBot 🌦️

A relatively simple weather bot developed for Discord.

![WeatherBot in action](https://imgur.com/a/Oy8lkCJ)
---

## ✨ Features

- **Current Weather Overview**: Get the temperature, "feels like" temperature, and humidity.
- **Hourly Rain Forecast**: See the chance of rain for the next 12 hours, hour by hour.
- **Wind Conditions**: Check the current wind speed and direction.
- **Location Specificity**: Supports specifying a state for US locations to improve accuracy (e.g., Cypress, CA vs. Cypress, TX).

---

## 🤖 Commands

WeatherBot uses Discord's built-in slash commands. Just type `/` to see all available commands.

- ### `/overview city:<city> [state:<state>]`
  Displays the main weather overview for a specified location. The `state` parameter is optional but recommended for US cities.
  > **Example**: `/overview city:Seattle state:WA`

- ### `/rain city:<city> [state:<state>]`
  Shows a 12-hour hourly forecast, listing only the hours with a significant chance of rain.
  > **Example**: `/rain city:Miami state:FL`

- ### `/wind city:<city> [state:<state>]`
  Provides the current wind speed and direction for a location.
  > **Example**: `/wind city:Chicago state:IL`

---
