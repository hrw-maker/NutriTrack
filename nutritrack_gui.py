# NutriTrack Fitness Planner GUI

import customtkinter as ctk
from tkinter import messagebox
import json
import os


DATA_FILE = "nutritrack_data.json"


def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
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


def split_meals(protein, carbs, fat, target_calories):
    return {
        "Breakfast": {
            "calories": round(target_calories * 0.30),
            "protein": round(protein * 0.30),
            "carbs": round(carbs * 0.30),
            "fat": round(fat * 0.30)
        },
        "Lunch": {
            "calories": round(target_calories * 0.35),
            "protein": round(protein * 0.35),
            "carbs": round(carbs * 0.35),
            "fat": round(fat * 0.35)
        },
        "Dinner": {
            "calories": round(target_calories * 0.35),
            "protein": round(protein * 0.35),
            "carbs": round(carbs * 0.35),
            "fat": round(fat * 0.35)
        }
    }


def get_level(points):
    if points < 30:
        return "Beginner"
    elif points < 70:
        return "Consistent Eater"
    elif points < 120:
        return "Fitness Learner"
    return "Nutrition Master"


class NutriTrackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NutriTrack Fitness Planner")
        self.root.geometry("1050x850")
        self.root.resizable(True, True)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.data = None
        self.meal_buttons = {}

        self.colors = {
            "background": "#F4F7EF",
            "card": "#FFFFFF",
            "green": "#1F7A3A",
            "dark_green": "#154D2A",
            "soft_green": "#EAF4E7",
            "orange": "#F4A261",
            "blue": "#DDEEFF",
            "text": "#1F2933",
            "muted": "#6B7280"
        }

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.root.configure(fg_color=self.colors["background"])

        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["background"],
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True, padx=25, pady=20)

        self.create_header()
        self.create_goal_bar()
        self.create_content_area()
        self.create_bottom_area()

    def create_header(self):
        header = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["background"]
        )
        header.pack(fill="x", pady=(0, 15))

        title_area = ctk.CTkFrame(header, fg_color=self.colors["background"])
        title_area.pack(side="left")

        title = ctk.CTkLabel(
            title_area,
            text="🌿 NutriTrack",
            font=("Arial", 38, "bold"),
            text_color=self.colors["dark_green"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_area,
            text="Your Simple Fitness Meal Planner",
            font=("Arial", 17),
            text_color=self.colors["dark_green"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        slogan = ctk.CTkLabel(
            header,
            text="Good food,\nbetter you 💪",
            font=("Arial", 16, "bold"),
            text_color=self.colors["dark_green"],
            justify="center"
        )
        slogan.pack(side="right", padx=30)

    def create_goal_bar(self):
        goal_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["soft_green"],
            border_color=self.colors["green"],
            border_width=2,
            corner_radius=18
        )
        goal_frame.pack(fill="x", pady=(0, 20), ipady=12)

        goal_label = ctk.CTkLabel(
            goal_frame,
            text="GOAL",
            font=("Arial", 16, "bold"),
            text_color=self.colors["dark_green"]
        )
        goal_label.pack(side="left", padx=30)

        self.goal_var = ctk.StringVar(value="Fat Loss")

        fat_button = ctk.CTkRadioButton(
            goal_frame,
            text="🔥 Fat Loss",
            variable=self.goal_var,
            value="Fat Loss",
            font=("Arial", 15, "bold"),
            text_color=self.colors["text"],
            fg_color=self.colors["green"],
            border_color=self.colors["green"]
        )
        fat_button.pack(side="left", padx=20)

        muscle_button = ctk.CTkRadioButton(
            goal_frame,
            text="🏋️ Muscle Gain",
            variable=self.goal_var,
            value="Muscle Gain",
            font=("Arial", 15, "bold"),
            text_color=self.colors["text"],
            fg_color=self.colors["green"],
            border_color=self.colors["green"]
        )
        muscle_button.pack(side="left", padx=20)

    def create_content_area(self):
        content = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["background"]
        )
        content.pack(fill="both", expand=True)

        left_column = ctk.CTkFrame(
            content,
            fg_color=self.colors["background"]
        )
        left_column.pack(side="left", fill="y", padx=(0, 18))

        right_column = ctk.CTkFrame(
            content,
            fg_color=self.colors["background"]
        )
        right_column.pack(side="left", fill="both", expand=True)

        self.create_user_card(left_column)
        self.create_target_card(left_column)
        self.create_meal_plan_card(right_column)

    def create_user_card(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=18,
            border_width=1,
            border_color="#D9E2D0"
        )
        card.pack(fill="x", pady=(0, 16), ipadx=15, ipady=15)

        title = ctk.CTkLabel(
            card,
            text="👤 USER INFO",
            font=("Arial", 17, "bold"),
            text_color=self.colors["dark_green"]
        )
        title.pack(anchor="w", padx=18, pady=(12, 10))

        self.name_entry = self.create_input(card, "Name", "")
        self.age_entry = self.create_input(card, "Age", "")
        self.height_entry = self.create_input(card, "Height cm", "")
        self.weight_entry = self.create_input(card, "Weight kg", "")

        self.gender_var = ctk.StringVar(value="Male")
        self.gender_menu = self.create_option(card, "Gender", self.gender_var, ["Male", "Female"])

        self.training_var = ctk.StringVar(value="Moderate training")
        self.training_menu = self.create_option(
            card,
            "Training Level",
            self.training_var,
            ["No training", "Light training", "Moderate training", "Heavy training"]
        )

        generate_button = ctk.CTkButton(
            card,
            text="Calculate Plan",
            height=42,
            fg_color=self.colors["green"],
            hover_color=self.colors["dark_green"],
            font=("Arial", 15, "bold"),
            command=self.generate_plan
        )
        generate_button.pack(fill="x", padx=18, pady=(15, 8))

        reset_button = ctk.CTkButton(
            card,
            text="Reset All Data",
            height=36,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=self.colors["text"],
            font=("Arial", 13, "bold"),
            command=self.reset_data
        )
        reset_button.pack(fill="x", padx=18, pady=(0, 15))

    def create_input(self, parent, label_text, default_text):
        row = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        row.pack(fill="x", padx=18, pady=6)

        label = ctk.CTkLabel(
            row,
            text=label_text,
            width=100,
            anchor="w",
            font=("Arial", 14),
            text_color=self.colors["text"]
        )
        label.pack(side="left")

        entry = ctk.CTkEntry(
            row,
            width=140,
            height=34,
            corner_radius=10
        )
        entry.pack(side="right")
        entry.insert(0, default_text)
        return entry

    def create_option(self, parent, label_text, variable, options):
        row = ctk.CTkFrame(parent, fg_color=self.colors["card"])
        row.pack(fill="x", padx=18, pady=6)

        label = ctk.CTkLabel(
            row,
            text=label_text,
            width=100,
            anchor="w",
            font=("Arial", 14),
            text_color=self.colors["text"]
        )
        label.pack(side="left")

        menu = ctk.CTkOptionMenu(
            row,
            values=options,
            variable=variable,
            width=140,
            height=34,
            fg_color=self.colors["green"],
            button_color=self.colors["dark_green"],
            button_hover_color=self.colors["dark_green"]
        )
        menu.pack(side="right")
        return menu

    def create_target_card(self, parent):
        self.target_card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=18,
            border_width=1,
            border_color="#D9E2D0"
        )
        self.target_card.pack(fill="x", ipadx=15, ipady=15)

        title = ctk.CTkLabel(
            self.target_card,
            text="🎯 DAILY TARGET",
            font=("Arial", 17, "bold"),
            text_color=self.colors["dark_green"]
        )
        title.pack(anchor="w", padx=18, pady=(12, 10))

        self.calorie_label = ctk.CTkLabel(
            self.target_card,
            text="Calories     -- kcal",
            font=("Arial", 18, "bold"),
            text_color=self.colors["text"]
        )
        self.calorie_label.pack(anchor="w", padx=20, pady=8)

        self.protein_label = ctk.CTkLabel(
            self.target_card,
            text="Protein      -- g",
            font=("Arial", 17, "bold"),
            text_color=self.colors["green"]
        )
        self.protein_label.pack(anchor="w", padx=20, pady=8)

        self.carbs_label = ctk.CTkLabel(
            self.target_card,
            text="Carbs        -- g",
            font=("Arial", 17, "bold"),
            text_color="#2456A6"
        )
        self.carbs_label.pack(anchor="w", padx=20, pady=8)

        self.fat_label = ctk.CTkLabel(
            self.target_card,
            text="Fat          -- g",
            font=("Arial", 17, "bold"),
            text_color="#C47A00"
        )
        self.fat_label.pack(anchor="w", padx=20, pady=8)

        self.bmr_tdee_label = ctk.CTkLabel(
            self.target_card,
            text="BMR and TDEE will appear here.",
            font=("Arial", 12),
            text_color=self.colors["muted"]
        )
        self.bmr_tdee_label.pack(anchor="w", padx=20, pady=(5, 15))

    def create_meal_plan_card(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=18,
            border_width=1,
            border_color="#D9E2D0"
        )
        card.pack(fill="both", expand=True, ipadx=15, ipady=15)

        title = ctk.CTkLabel(
            card,
            text="🍽️ MEAL PLAN",
            font=("Arial", 18, "bold"),
            text_color=self.colors["dark_green"]
        )
        title.pack(anchor="w", padx=18, pady=(12, 10))

        self.meals_frame = ctk.CTkFrame(card, fg_color=self.colors["card"])
        self.meals_frame.pack(fill="both", expand=True, padx=12, pady=5)

        self.meal_cards = {}

        self.create_single_meal_card(
            self.meals_frame,
            "Breakfast",
            "🥣",
            "#FFF6D8"
        )
        self.create_single_meal_card(
            self.meals_frame,
            "Lunch",
            "🍗",
            "#EEF8E8"
        )
        self.create_single_meal_card(
            self.meals_frame,
            "Dinner",
            "🍣",
            "#EAF3FF"
        )

    def create_single_meal_card(self, parent, meal_name, icon, color):
        meal_card = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=16,
            border_width=1,
            border_color="#D0D7C8"
        )
        meal_card.pack(fill="x", padx=5, pady=9, ipady=10)

        top = ctk.CTkFrame(meal_card, fg_color=color)
        top.pack(fill="x", padx=16, pady=(10, 5))

        meal_title = ctk.CTkLabel(
            top,
            text=icon + "  " + meal_name,
            font=("Arial", 20, "bold"),
            text_color=self.colors["text"]
        )
        meal_title.pack(side="left")

        button = ctk.CTkButton(
            top,
            text="Not Completed",
            width=130,
            height=38,
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color=self.colors["text"],
            command=lambda: self.complete_meal(meal_name)
        )
        button.pack(side="right")

        details = ctk.CTkLabel(
            meal_card,
            text="Calories -- kcal     Protein -- g     Carbs -- g     Fat -- g",
            font=("Arial", 15),
            text_color=self.colors["text"]
        )
        details.pack(anchor="w", padx=20, pady=(8, 10))

        self.meal_cards[meal_name] = details
        self.meal_buttons[meal_name] = button

    def create_bottom_area(self):
        bottom = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors["background"]
        )
        bottom.pack(fill="x", pady=(15, 0))

        progress_card = ctk.CTkFrame(
            bottom,
            fg_color=self.colors["card"],
            corner_radius=18,
            border_width=1,
            border_color="#D9E2D0"
        )
        progress_card.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=12)

        progress_title = ctk.CTkLabel(
            progress_card,
            text="📈 TRACK YOUR PROGRESS",
            font=("Arial", 16, "bold"),
            text_color=self.colors["dark_green"]
        )
        progress_title.pack(anchor="w", padx=18, pady=(10, 8))

        weight_row = ctk.CTkFrame(progress_card, fg_color=self.colors["card"])
        weight_row.pack(fill="x", padx=18)

        self.new_weight_entry = ctk.CTkEntry(
            weight_row,
            placeholder_text="Today's weight kg",
            width=180,
            height=36
        )
        self.new_weight_entry.pack(side="left", padx=(0, 10))

        record_button = ctk.CTkButton(
            weight_row,
            text="Record Weight",
            width=140,
            height=36,
            fg_color=self.colors["green"],
            hover_color=self.colors["dark_green"],
            command=self.record_weight
        )
        record_button.pack(side="left")

        self.progress_label = ctk.CTkLabel(
            progress_card,
            text="Points: 0 | Level: Beginner | Completed Days: 0",
            font=("Arial", 14, "bold"),
            text_color=self.colors["text"]
        )
        self.progress_label.pack(anchor="w", padx=18, pady=(12, 2))

        self.feedback_label = ctk.CTkLabel(
            progress_card,
            text="Weight feedback will appear here.",
            font=("Arial", 13),
            text_color=self.colors["muted"]
        )
        self.feedback_label.pack(anchor="w", padx=18, pady=(2, 10))

        reward_card = ctk.CTkFrame(
            bottom,
            fg_color=self.colors["soft_green"],
            corner_radius=18,
            border_width=1,
            border_color="#B7D7B0"
        )
        reward_card.pack(side="right", fill="x", expand=True, padx=(12, 0), ipady=12)

        self.reward_label = ctk.CTkLabel(
            reward_card,
            text="🏆 Great Job!",
            font=("Arial", 24, "bold"),
            text_color=self.colors["dark_green"]
        )
        self.reward_label.pack(pady=(18, 5))

        self.reward_text = ctk.CTkLabel(
            reward_card,
            text="Complete all meals today to earn points.",
            font=("Arial", 14),
            text_color=self.colors["text"]
        )
        self.reward_text.pack(pady=(0, 18))

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
        meals = split_meals(protein, carbs, fat, target_calories)

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
        if self.data is None:
            return

        plan = self.data["plan"]

        self.calorie_label.configure(
            text="🔥 Calories     " + str(plan["target_calories"]) + " kcal"
        )
        self.protein_label.configure(
            text="🥩 Protein      " + str(plan["protein"]) + " g"
        )
        self.carbs_label.configure(
            text="🍚 Carbs        " + str(plan["carbs"]) + " g"
        )
        self.fat_label.configure(
            text="🥑 Fat          " + str(plan["fat"]) + " g"
        )
        self.bmr_tdee_label.configure(
            text="BMR: " + str(plan["bmr"]) + " kcal | TDEE: " + str(plan["tdee"]) + " kcal"
        )

        for meal, macros in plan["meals"].items():
            text = (
                "Calories " + str(macros["calories"]) + " kcal     "
                "Protein " + str(macros["protein"]) + " g     "
                "Carbs " + str(macros["carbs"]) + " g     "
                "Fat " + str(macros["fat"]) + " g"
            )
            self.meal_cards[meal].configure(text=text)

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
            self.reward_label.configure(text="🏆 Great Job!")
            self.reward_text.configure(
                text="You completed all your meals today!\nKeep it up and stay consistent 💪"
            )
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

        self.feedback_label.configure(
            text="Weight change: " + str(round(difference, 2)) + " kg. " + feedback
        )

        self.reward_label.configure(text="🏆 New Day Started")
        self.reward_text.configure(text="Complete all meals today to earn points.")

        self.save_data()
        self.display_plan()
        self.update_checkin_buttons()
        self.update_progress()

        messagebox.showinfo("Weight Recorded", "Weight has been recorded. A new day has started.")

    def update_checkin_buttons(self):
        if self.data is None:
            for meal in self.meal_buttons:
                self.meal_buttons[meal].configure(
                    text="Not Completed",
                    fg_color="#E5E7EB",
                    text_color=self.colors["text"]
                )
            return

        for meal in self.meal_buttons:
            if self.data["checkin"][meal]:
                self.meal_buttons[meal].configure(
                    text="✓ Completed",
                    fg_color=self.colors["green"],
                    text_color="white"
                )
            else:
                self.meal_buttons[meal].configure(
                    text="Not Completed",
                    fg_color="#E5E7EB",
                    text_color=self.colors["text"]
                )

    def update_progress(self):
        if self.data is None:
            self.progress_label.configure(text="Points: 0 | Level: Beginner | Completed Days: 0")
            return

        points = self.data["points"]
        completed_days = self.data["completed_days"]
        level = get_level(points)

        self.progress_label.configure(
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

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, user["name"])

        self.age_entry.delete(0, "end")
        self.age_entry.insert(0, str(user["age"]))

        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, str(user["height"]))

        self.weight_entry.delete(0, "end")
        self.weight_entry.insert(0, str(user["weight"]))

        self.gender_var.set(user["gender"])
        self.goal_var.set(user["goal"])
        self.training_var.set(user["training"])

    def reset_data(self):
        answer = messagebox.askyesno("Reset Data", "Are you sure you want to delete all saved data?")

        if answer:
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)

            self.data = None

            self.name_entry.delete(0, "end")
            self.age_entry.delete(0, "end")
            self.height_entry.delete(0, "end")
            self.weight_entry.delete(0, "end")
            self.new_weight_entry.delete(0, "end")

            self.gender_var.set("Male")
            self.goal_var.set("Fat Loss")
            self.training_var.set("Moderate training")

            self.calorie_label.configure(text="Calories     -- kcal")
            self.protein_label.configure(text="Protein      -- g")
            self.carbs_label.configure(text="Carbs        -- g")
            self.fat_label.configure(text="Fat          -- g")
            self.bmr_tdee_label.configure(text="BMR and TDEE will appear here.")

            for meal in self.meal_cards:
                self.meal_cards[meal].configure(
                    text="Calories -- kcal     Protein -- g     Carbs -- g     Fat -- g"
                )

            self.feedback_label.configure(text="Weight feedback will appear here.")
            self.reward_label.configure(text="🏆 Great Job!")
            self.reward_text.configure(text="Complete all meals today to earn points.")

            self.update_checkin_buttons()
            self.update_progress()

            messagebox.showinfo("Reset Complete", "All data has been deleted.")


def main():
    root = ctk.CTk()
    NutriTrackApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
