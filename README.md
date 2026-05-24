# NutriTrack Fitness Planner

NutriTrack is a simple fitness nutrition planner built with Python. It uses a modern graphical user interface to help users calculate their daily calorie target, macronutrients, meal plan, and progress.

The project is designed for people who want a simple way to manage their daily nutrition for either fat loss or muscle gain.

## Main File

nutritrack_gui.py

## How to Run

This project uses `customtkinter`, so you need to install it before running the program.

Install `customtkinter`:

```bash
pip install customtkinter
```

Run the program:

```bash
python3 nutritrack_gui.py
```

## Run with Virtual Environment on Mac

If `pip install customtkinter` does not work on Mac, use a virtual environment.

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install `customtkinter`:

```bash
pip install customtkinter
```

Run the program:

```bash
python nutritrack_gui.py
```

## Important Note

This project uses `customtkinter` to create a graphical user interface.

The Ed online terminal may not support GUI windows, so it may show a DISPLAY environment error. Please run the program locally on a computer that supports GUI applications.

## Description

NutriTrack is a fitness nutrition planner with a colored graphical user interface.

Users can enter their personal information, including name, age, gender, height, weight, fitness goal, and training level. The program then calculates the user's BMR, TDEE, daily target calories, protein, carbohydrates, and fat.

The program also divides the daily nutrition targets into breakfast, lunch, and dinner. This helps users understand how much they should aim to eat for each meal.

NutriTrack also includes meal check-in buttons. Users can mark breakfast, lunch, and dinner as completed. When all three meals are completed, the user receives a reward message and earns points.

Users can also record their body weight progress. The program compares the new weight with the previous weight and gives feedback based on the user's goal.

## Main Features

- Modern colored GUI using `customtkinter`
- Goal selection for Fat Loss or Muscle Gain
- User information input
- BMR calculation
- TDEE calculation
- Daily calorie target calculation
- Protein, carbohydrates, and fat calculation
- Breakfast, lunch, and dinner meal plan
- Meal completion check-ins
- Reward points system
- Body weight progress recording
- Local data saving with JSON

## Files

nutritrack_gui.py - Main Python program  
nutritrack_data.json - Saved user data, created automatically after running  
README.md - Project description and running instructions  

## Possible Issue

If the program shows this error:

```text
ModuleNotFoundError: No module named 'customtkinter'
```

It means `customtkinter` has not been installed.

Install it with:

```bash
pip install customtkinter
```

If you are using Mac and this does not work, use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install customtkinter
python nutritrack_gui.py
```

## Project Purpose

The purpose of NutriTrack is to provide a simple and beginner-friendly fitness nutrition tool. It helps users understand their daily energy needs and follow a basic meal plan without using complicated fitness apps.

This project also demonstrates Python GUI programming, user input handling, basic nutrition calculations, condition checking, progress tracking, and local data storage.
