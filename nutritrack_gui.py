# NutriTrack Fitness Planner GUI
# Run this file with: python3 smartbite_gui.py

import tkinter as tk
from tkinter import messagebox
import json
import os


DATA_FILE = "nutritrack_data.json"


def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_tdee(bmr, training_level):
    factors = {
        "No training": 1.2,
        "Light training": 1.375,
        "Moderate training": 1.55,
        "Heavy training": 1.725
    }
    return bmr * factors[training_level]


def calculate_target_calories(tdee, goal):
    if goal == "Fat Loss":
        return tdee - 400
    else:
        return tdee + 300


def calculate_macros(weight, target_calories, goal):
    if goal == "Fat Loss":
        protein = weight * 2.0
        fat = weight * 0.8
    else:
        protein = weight * 1.8
        fat = weight * 1.0

    protein_calories = protein * 4
    fat_calories = fat * 9
    carbs = (target_calories - protein_calories - fat_calories) / 4

    if carbs < 0:
        carbs = 0

    return round(protein), round(carbs), round(fat)


def split_meals(protein, carbs, fat):
    return {
        "Breakfast": {
            "protein": round(protein * 0.3),
            "carbs": round(carbs * 0.3),
            "fat": round(fat * 0.3)
        },
        "Lunch": {
            "protein": round(protein * 0.4),
            "carbs": round(carbs * 0.4),
            "fat": round(fat * 0.4)
        },
        "Dinner": {
            "protein": round(protein * 0.3),
            "carbs": round(carbs * 0.3),
            "fat": round(fat * 0.3)
        }
    }


def get_level(points):
    if points < 30:
        return "Beginner"
    elif points < 70:
        return "Consistent Eater"
    elif points < 120:
        return "Fitness Learner"
    else:
        return "Nutrition Master"


class NutriTrackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NutriTrack Fitness Planner")
        self.root.geometry("760x720")

        self.data = None

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="NutriTrack Fitness Planner",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=15)

        subtitle = tk.Label(
            self.root,
            text="A simple nutrition planner for muscle gain and fat loss",
            font=("Arial", 12)
        )
        subtitle.pack(pady=5)

        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10)

        left_frame = tk.LabelFrame(main_frame, text="User Profile", padx=15, pady=15)
        left_frame.grid(row=0, column=0, padx=15, sticky="n")

        right_frame = tk.LabelFrame(main_frame, text="Nutrition Plan", padx=15, pady=15)
        right_frame.grid(row=0, column=1, padx=15, sticky="n")

        tk.Label(left_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(left_frame, width=25)
        self.name_entry.grid(row=0, column=1, pady=5)

        tk.Label(left_frame, text="Age:").grid(row=1, column=0, sticky="w", pady=5)
        self.age_entry = tk.Entry(left_frame, width=25)
        self.age_entry.grid(row=1, column=1, pady=5)

        tk.Label(left_frame, text="Gender:").grid(row=2, column=0, sticky="w", pady=5)
        self.gender_var = tk.StringVar(value="Male")
        gender_menu = tk.OptionMenu(left_frame, self.gender_var, "Male", "Female")
        gender_menu.grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(left_frame, text="Height cm:").grid(row=3, column=0, sticky="w", pady=5)
        self.height_entry = tk.Entry(left_frame, width=25)
        self.height_entry.grid(row=3, column=1, pady=5)

        tk.Label(left_frame, text="Weight kg:").grid(row=4, column=0, sticky="w", pady=5)
        self.weight_entry = tk.Entry(left_frame, width=25)
        self.weight_entry.grid(row=4, column=1, pady=5)

        tk.Label(left_frame, text="Goal:").grid(row=5, column=0, sticky="w", pady=5)
        self.goal_var = tk.StringVar(value="Fat Loss")
        goal_menu = tk.OptionMenu(left_frame, self.goal_var, "Fat Loss", "Muscle Gain")
        goal_menu.grid(row=5, column=1, sticky="w", pady=5)

        tk.Label(left_frame, text="Training:").grid(row=6, column=0, sticky="w", pady=5)
        self.training_var = tk.StringVar(value="Moderate training")
        training_menu = tk.OptionMenu(
            left_frame,
            self.training_var,
            "No training",
            "Light training",
            "Moderate training",
            "Heavy training"
        )
        training_menu.grid(row=6, column=1, sticky="w", pady=5)

        generate_button = tk.Button(
            left_frame,
            text="Generate Nutrition Plan",
            width=25,
            command=self.generate_plan
        )
        generate_button.grid(row=7, column=0, columnspan=2, pady=15)

        reset_button = tk.Button(
            left_frame,
            text="Reset All Data",
            width=25,
            command=self.reset_data
        )
        reset_button.grid(row=8, column=0, columnspan=2, pady=5)

        self.plan_text = tk.Text(right_frame, width=42, height=22)
        self.plan_text.pack()

        checkin_frame = tk.LabelFrame(self.root, text="Daily Meal Check-in", padx=15, pady=15)
        checkin_frame.pack(pady=10)

        self.breakfast_button = tk.Button(
            checkin_frame,
            text="Breakfast Not Completed",
            width=25,
            command=lambda: self.complete_meal("Breakfast")
        )
        self.breakfast_button.grid(row=0, column=0, padx=8, pady=5)

        self.lunch_button = tk.Button(
            checkin_frame,
            text="Lunch Not Completed",
            width=25,
            command=lambda: self.complete_meal("Lunch")
        )
        self.lunch_button.grid(row=0, column=1, padx=8, pady=5)

        self.dinner_button = tk.Button(
            checkin_frame,
            text="Dinner Not Completed",
            width=25,
            command=lambda: self.complete_meal("Dinner")
        )
        self.dinner_button.grid(row=0, column=2, padx=8, pady=5)

        progress_frame = tk.LabelFrame(self.root, text="Progress Tracking", padx=15, pady=15)
        progress_frame.pack(pady=10)

        tk.Label(progress_frame, text="Today's Weight kg:").grid(row=0, column=0, padx=5)
        self.new_weight_entry = tk.Entry(progress_frame, width=15)
        self.new_weight_entry.grid(row=0, column=1, padx=5)

        record_button = tk.Button(
            progress_frame,
            text="Record Weight",
            width=20,
            command=self.record_weight
        )
        record_button.grid(row=0, column=2, padx=10)

        self.progress_label = tk.Label(
            progress_frame,
            text="Points: 0 | Level: Beginner | Completed Days: 0",
            font=("Arial", 12)
        )
        self.progress_label.grid(row=1, column=0, columnspan=3, pady=10)

        self.feedback_label = tk.Label(
            progress_frame,
            text="Weight feedback will appear here.",
            font=("Arial", 11)
        )
        self.feedback_label.grid(row=2, column=0, columnspan=3, pady=5)

    def generate_plan(self):
        try:
            name = self.name_entry.get().strip()
            age = int(self.age_entry.get())
            height = float(self.height_entry.get())
            weight = float(self.weight_entry.get())
            gender = self.gender_var.get()
            goal = self.goal_var.get()
            training = self.training_var.get()

            if name == "":
                messagebox.showerror("Input Error", "Name cannot be empty.")
                return

            if age <= 0 or height <= 0 or weight <= 0:
                messagebox.showerror("Input Error", "Age, height, and weight must be positive.")
                return

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for age, height, and weight.")
            return

        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, training)
        target_calories = calculate_target_calories(tdee, goal)
        protein, carbs, fat = calculate_macros(weight, target_calories, goal)
        meals = split_meals(protein, carbs, fat)

        self.data = {
            "user": {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "goal": goal,
                "training": training
            },
            "plan": {
                "bmr": round(bmr),
                "tdee": round(tdee),
                "target_calories": round(target_calories),
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                "meals": meals
            },
            "checkin": {
                "Breakfast": False,
                "Lunch": False,
                "Dinner": False
            },
            "points": 0,
            "completed_days": 0,
            "weight_history": [weight]
        }

        self.save_data()
        self.display_plan()
        self.update_checkin_buttons()
        self.update_progress()

        messagebox.showinfo("Success", "Your nutrition plan has been generated.")

    def display_plan(self):
        self.plan_text.delete("1.0", tk.END)

        if self.data is None:
            self.plan_text.insert(tk.END, "No nutrition plan yet.")
            return

        user = self.data["user"]
        plan = self.data["plan"]

        text = ""
        text += "User Profile\n"
        text += "-" * 35 + "\n"
        text += "Name: " + user["name"] + "\n"
        text += "Age: " + str(user["age"]) + "\n"
        text += "Gender: " + user["gender"] + "\n"
        text += "Height: " + str(user["height"]) + " cm\n"
        text += "Weight: " + str(user["weight"]) + " kg\n"
        text += "Goal: " + user["goal"] + "\n"
        text += "Training: " + user["training"] + "\n\n"

        text += "Daily Nutrition Target\n"
        text += "-" * 35 + "\n"
        text += "BMR: " + str(plan["bmr"]) + " kcal\n"
        text += "TDEE: " + str(plan["tdee"]) + " kcal\n"
        text += "Target Calories: " + str(plan["target_calories"]) + " kcal\n"
        text += "Protein: " + str(plan["protein"]) + " g\n"
        text += "Carbs: " + str(plan["carbs"]) + " g\n"
        text += "Fat: " + str(plan["fat"]) + " g\n\n"

        text += "Meal Distribution\n"
        text += "-" * 35 + "\n"

        for meal, macros in plan["meals"].items():
            text += meal + ":\n"
            text += "  Protein: " + str(macros["protein"]) + " g\n"
            text += "  Carbs: " + str(macros["carbs"]) + " g\n"
            text += "  Fat: " + str(macros["fat"]) + " g\n"

        self.plan_text.insert(tk.END, text)

    def complete_meal(self, meal):
        if self.data is None:
            messagebox.showwarning("No Profile", "Please generate a nutrition plan first.")
            return

        if self.data["checkin"][meal]:
            messagebox.showinfo("Already Completed", meal + " has already been completed.")
            return

        self.data["checkin"][meal] = True

        if all(self.data["checkin"].values()):
            self.data["points"] += 10
            self.data["completed_days"] += 1
            messagebox.showinfo(
                "Congratulations",
                "You completed all three meals today and earned 10 points!"
            )

        self.save_data()
        self.update_checkin_buttons()
        self.update_progress()

    def record_weight(self):
        if self.data is None:
            messagebox.showwarning("No Profile", "Please generate a nutrition plan first.")
            return

        try:
            current_weight = float(self.new_weight_entry.get())

            if current_weight <= 0:
                messagebox.showerror("Input Error", "Weight must be positive.")
                return

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid weight.")
            return

        previous_weight = self.data["weight_history"][-1]
        difference = current_weight - previous_weight
        goal = self.data["user"]["goal"]

        self.data["weight_history"].append(current_weight)
        self.data["user"]["weight"] = current_weight

        if goal == "Fat Loss":
            if difference < -0.1:
                feedback = "Good progress! Your weight decreased."
            elif -0.1 <= difference <= 0.1:
                feedback = "Your weight stayed almost the same. Keep following the plan."
            else:
                feedback = "Your weight increased. You may need to check your calorie intake."
        else:
            if difference > 0.1:
                feedback = "Good progress! Your weight increased."
            elif -0.1 <= difference <= 0.1:
                feedback = "Your weight stayed almost the same. You may need to eat slightly more."
            else:
                feedback = "Your weight decreased. You may not be eating enough."

        self.data["checkin"] = {
            "Breakfast": False,
            "Lunch": False,
            "Dinner": False
        }

        self.feedback_label.config(
            text="Weight change: " + str(round(difference, 2)) + " kg. " + feedback
        )

        self.save_data()
        self.display_plan()
        self.update_checkin_buttons()
        self.update_progress()

        messagebox.showinfo("Weight Recorded", "Weight has been recorded. A new day has started.")

    def update_checkin_buttons(self):
        if self.data is None:
            return

        if self.data["checkin"]["Breakfast"]:
            self.breakfast_button.config(text="Breakfast Completed")
        else:
            self.breakfast_button.config(text="Breakfast Not Completed")

        if self.data["checkin"]["Lunch"]:
            self.lunch_button.config(text="Lunch Completed")
        else:
            self.lunch_button.config(text="Lunch Not Completed")

        if self.data["checkin"]["Dinner"]:
            self.dinner_button.config(text="Dinner Completed")
        else:
            self.dinner_button.config(text="Dinner Not Completed")

    def update_progress(self):
        if self.data is None:
            self.progress_label.config(text="Points: 0 | Level: Beginner | Completed Days: 0")
            return

        points = self.data["points"]
        completed_days = self.data["completed_days"]
        level = get_level(points)

        self.progress_label.config(
            text="Points: " + str(points) +
                 " | Level: " + level +
                 " | Completed Days: " + str(completed_days)
        )

    def save_data(self):
        with open(DATA_FILE, "w") as file:
            json.dump(self.data, file, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as file:
                    self.data = json.load(file)

                self.fill_profile_entries()
                self.display_plan()
                self.update_checkin_buttons()
                self.update_progress()

            except json.JSONDecodeError:
                self.data = None
                messagebox.showwarning("Data Error", "Saved data is damaged.")

    def fill_profile_entries(self):
        if self.data is None:
            return

        user = self.data["user"]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, user["name"])

        self.age_entry.delete(0, tk.END)
        self.age_entry.insert(0, str(user["age"]))

        self.gender_var.set(user["gender"])

        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(user["height"]))

        self.weight_entry.delete(0, tk.END)
        self.weight_entry.insert(0, str(user["weight"]))

        self.goal_var.set(user["goal"])
        self.training_var.set(user["training"])

    def reset_data(self):
        answer = messagebox.askyesno("Reset Data", "Are you sure you want to delete all saved data?")

        if answer:
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)

            self.data = None

            self.name_entry.delete(0, tk.END)
            self.age_entry.delete(0, tk.END)
            self.height_entry.delete(0, tk.END)
            self.weight_entry.delete(0, tk.END)
            self.new_weight_entry.delete(0, tk.END)

            self.gender_var.set("Male")
            self.goal_var.set("Fat Loss")
            self.training_var.set("Moderate training")

            self.plan_text.delete("1.0", tk.END)
            self.plan_text.insert(tk.END, "No nutrition plan yet.")

            self.breakfast_button.config(text="Breakfast Not Completed")
            self.lunch_button.config(text="Lunch Not Completed")
            self.dinner_button.config(text="Dinner Not Completed")

            self.feedback_label.config(text="Weight feedback will appear here.")
            self.update_progress()

            messagebox.showinfo("Reset Complete", "All data has been deleted.")


def main():
    root = tk.Tk()
    app = NutriTrackApp(root)
    root.mainloop()


main()

