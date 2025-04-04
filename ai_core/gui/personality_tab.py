import tkinter as tk
from tkinter import ttk, scrolledtext
import logging

class PersonalityTab(ttk.Frame):
    """
    Frame containing the personality customization tabs.
    """
    def __init__(self, parent_notebook, main_app_instance, **kwargs):
        print("PersonalityTab: Initializing...")
        super().__init__(parent_notebook, **kwargs)
        self.parent = parent_notebook
        self.main_app = main_app_instance # Reference to the main app instance
        self.logger = logging.getLogger(__name__)

        # Personality Settings Store - Managed within this class now
        self.personality_settings = {}
        # We will store tk variables here to easily access/save settings
        self._personality_vars = {}

        self._create_widgets()
        print("PersonalityTab: Initialization complete")

    def _create_widgets(self):
        """Creates the main Personality customization tab with sub-tabs."""
        # Sub-notebook for different sections
        self.sub_notebook = ttk.Notebook(self)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create frames for each sub-tab
        profile_frame = ttk.Frame(self.sub_notebook)
        quirks_frame = ttk.Frame(self.sub_notebook)
        questions_frame = ttk.Frame(self.sub_notebook)
        preferences_frame = ttk.Frame(self.sub_notebook)
        description_frame = ttk.Frame(self.sub_notebook)

        # Add frames to the sub-notebook
        self.sub_notebook.add(profile_frame, text="Profile")
        self.sub_notebook.add(quirks_frame, text="Quirks")
        self.sub_notebook.add(questions_frame, text="Questions")
        self.sub_notebook.add(preferences_frame, text="Preferences")
        self.sub_notebook.add(description_frame, text="Description")

        # Populate each sub-tab
        self._create_profile_subtab(profile_frame)
        self._create_quirks_subtab(quirks_frame)
        self._create_questions_subtab(questions_frame)
        self._create_preferences_subtab(preferences_frame)
        self._create_description_subtab(description_frame)

        # Apply/Save button (placed within this frame now)
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        apply_button = ttk.Button(button_frame, text="Apply Personality Settings", command=self._apply_personality_settings)
        apply_button.pack(side=tk.RIGHT)
        
        # Add a Save/Load profile button group
        save_button = ttk.Button(button_frame, text="Save Profile", command=self._save_personality)
        save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        load_button = ttk.Button(button_frame, text="Load Profile", command=self._load_personality)
        load_button.pack(side=tk.LEFT)

    def _create_profile_subtab(self, parent):
        """Populates the Profile sub-tab."""
        # Main container for profile settings
        profile_container = ttk.Frame(parent)
        profile_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column - Basic profile info
        left_frame = ttk.Frame(profile_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Name
        name_frame = ttk.Frame(left_frame)
        name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(name_frame, text="Name").grid(row=0, column=0, sticky="w", padx=5)
        self._personality_vars['name'] = tk.StringVar(value="")
        ttk.Entry(name_frame, textvariable=self._personality_vars['name']).grid(row=0, column=1, sticky="ew", padx=5)
        name_frame.columnconfigure(1, weight=1)
        
        # Nickname
        nickname_frame = ttk.Frame(left_frame)
        nickname_frame.pack(fill=tk.X, pady=2)
        ttk.Label(nickname_frame, text="Nickname").grid(row=0, column=0, sticky="w", padx=5)
        self._personality_vars['nickname'] = tk.StringVar(value="")
        ttk.Entry(nickname_frame, textvariable=self._personality_vars['nickname']).grid(row=0, column=1, sticky="ew", padx=5)
        nickname_frame.columnconfigure(1, weight=1)
        
        # Personality Type
        personality_frame = ttk.Frame(left_frame)
        personality_frame.pack(fill=tk.X, pady=2)
        ttk.Label(personality_frame, text="Personality").grid(row=0, column=0, sticky="w", padx=5)
        self._personality_vars['personality_type'] = tk.StringVar(value="")
        
        personality_entry = ttk.Entry(personality_frame, textvariable=self._personality_vars['personality_type'])
        personality_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Personality type picker button
        personality_picker = ttk.Button(personality_frame, text="...", width=3, 
                                      command=lambda: self._show_personality_picker())
        personality_picker.grid(row=0, column=2, padx=(0, 5))
        
        personality_frame.columnconfigure(1, weight=1)
        
        # Blood Type
        blood_frame = ttk.Frame(left_frame)
        blood_frame.pack(fill=tk.X, pady=2)
        ttk.Label(blood_frame, text="Blood Type").grid(row=0, column=0, sticky="w", padx=5)
        
        # Blood Type radiobuttons
        blood_type_frame = ttk.Frame(blood_frame)
        blood_type_frame.grid(row=0, column=1, sticky="w")
        
        self._personality_vars['blood_type'] = tk.StringVar(value="O")
        
        blood_types = ["A", "B", "O", "AB"]
        for i, blood_type in enumerate(blood_types):
            ttk.Radiobutton(blood_type_frame, text=blood_type, value=blood_type,
                           variable=self._personality_vars['blood_type']).grid(row=0, column=i, padx=10)
        
        # Birthday
        birthday_frame = ttk.Frame(left_frame)
        birthday_frame.pack(fill=tk.X, pady=2)
        ttk.Label(birthday_frame, text="Birthday").grid(row=0, column=0, sticky="w", padx=5)
        
        birthday_subframe = ttk.Frame(birthday_frame)
        birthday_subframe.grid(row=0, column=1, sticky="w")
        
        # Month dropdown
        self._personality_vars['birth_month'] = tk.IntVar(value=1)
        month_values = [i for i in range(1, 13)]
        month_dropdown = ttk.Combobox(birthday_subframe, textvariable=self._personality_vars['birth_month'],
                                     values=month_values, width=5)
        month_dropdown.grid(row=0, column=0, padx=(0, 5))
        ttk.Label(birthday_subframe, text="Month").grid(row=0, column=1, padx=(0, 10))
        
        # Day dropdown
        self._personality_vars['birth_day'] = tk.IntVar(value=1)
        day_values = [i for i in range(1, 32)]
        day_dropdown = ttk.Combobox(birthday_subframe, textvariable=self._personality_vars['birth_day'],
                                   values=day_values, width=5)
        day_dropdown.grid(row=0, column=2, padx=(0, 5))
        ttk.Label(birthday_subframe, text="Day").grid(row=0, column=3, sticky="w")
        
        # Club/Interest
        club_frame = ttk.Frame(left_frame)
        club_frame.pack(fill=tk.X, pady=2)
        ttk.Label(club_frame, text="Club").grid(row=0, column=0, sticky="w", padx=5)
        
        club_values = ["None", "Art", "Music", "Science", "Sports", "Literature", "Technology", "Cooking", "Gaming"]
        self._personality_vars['club'] = tk.StringVar(value="None")
        club_dropdown = ttk.Combobox(club_frame, textvariable=self._personality_vars['club'],
                                    values=club_values)
        club_dropdown.grid(row=0, column=1, sticky="ew", padx=5)
        club_frame.columnconfigure(1, weight=1)
        
        # Voice Pitch slider
        voice_frame = ttk.Frame(left_frame)
        voice_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(voice_frame, text="Voice Pitch (Low - High)").grid(row=0, column=0, sticky="w", padx=5)
        self._personality_vars['voice_pitch'] = tk.IntVar(value=50)
        
        voice_slider_frame = ttk.Frame(voice_frame)
        voice_slider_frame.grid(row=0, column=1, sticky="ew", padx=5)
        
        voice_slider = ttk.Scale(voice_slider_frame, variable=self._personality_vars['voice_pitch'], 
                               from_=0, to=100, orient=tk.HORIZONTAL)
        voice_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Display current value
        voice_value = ttk.Label(voice_slider_frame, text="50")
        voice_value.pack(side=tk.LEFT, padx=(0, 5))
        
        # Update label when slider changes
        def update_voice_value(event):
            voice_value.configure(text=str(self._personality_vars['voice_pitch'].get()))
        
        voice_slider.bind("<Motion>", update_voice_value)
        
        # Reset button for voice pitch
        voice_reset = ttk.Button(voice_slider_frame, text="Reset",
                               command=lambda: self._reset_voice_pitch())
        voice_reset.pack(side=tk.LEFT)
        
        voice_frame.columnconfigure(1, weight=1)
        
        # Author history
        history_frame = ttk.Frame(left_frame)
        history_frame.pack(fill=tk.X, pady=2)
        ttk.Label(history_frame, text="Author history").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(history_frame, text="[Empty]").grid(row=0, column=1, sticky="w", padx=5)
        
        # User nickname field
        user_frame = ttk.Frame(left_frame)
        user_frame.pack(fill=tk.X, pady=2)
        ttk.Label(user_frame, text="Your nickname").grid(row=0, column=0, sticky="w", padx=5)
        
        user_nickname_frame = ttk.Frame(user_frame)
        user_nickname_frame.grid(row=0, column=1, sticky="ew")
        user_frame.columnconfigure(1, weight=1)
        
        self._personality_vars['user_nickname'] = tk.StringVar(value="Anonymous")
        user_entry = ttk.Entry(user_nickname_frame, textvariable=self._personality_vars['user_nickname'])
        user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        user_reset = ttk.Button(user_nickname_frame, text="Reset",
                              command=lambda: self._reset_user_nickname())
        user_reset.pack(side=tk.LEFT)
        
        # Info text
        ttk.Label(left_frame, text="Your nickname will be saved to the profile and used in the AI's responses.").pack(pady=5)

    def _reset_voice_pitch(self):
        """Reset voice pitch to default (50)."""
        self._personality_vars['voice_pitch'].set(50)
        
    def _reset_user_nickname(self):
        """Reset user nickname to default (Anonymous)."""
        self._personality_vars['user_nickname'].set("Anonymous")
        
    def _show_personality_picker(self):
        """Show a dialog to pick a personality type."""
        picker_window = tk.Toplevel(self.main_app.root)
        picker_window.title("Select a personality type")
        picker_window.transient(self.main_app.root)
        picker_window.grab_set()
        
        # Make the window modal
        picker_window.geometry("400x500")
        
        # Add a frame with a nice background
        frame = ttk.Frame(picker_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a list of personality types
        personality_types = [
            "Flirt", "Heiress", "Snob", "Underclassman", 
            "Enigma", "Space Case", "Japanese Ideal", "Tomboy",
            "Pure Heart", "Girl Next Door", "Dark Lord", "Mother Figure",
            "Big Sister", "Airhead", "Rebel", "Wild Child",
            "Honor Student", "Sourpuss", "Misfortune Magnet", "Bookworm",
            "Scaredy Cat", "Classic Heroine", "Fangirl", "Geek",
            "Psycho Stalker", "Slacker", "Introvert", "Tough Girl",
            "Old School", "Loner", "Extrovert", "Athlete",
            "Angel", "Seductress", "French Girl", "The Brit",
            "Dominatrix", "Robo"
        ]
        
        # Create radio buttons for each personality type
        self._personality_vars['personality_picker'] = tk.StringVar(value=self._personality_vars['personality_type'].get() or "Pure Heart")
        
        # Create a scrollable frame for the radio buttons
        canvas = tk.Canvas(frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        # Create two columns of radio buttons
        col1_frame = ttk.Frame(scroll_frame)
        col1_frame.grid(row=0, column=0, padx=10)
        
        col2_frame = ttk.Frame(scroll_frame)
        col2_frame.grid(row=0, column=1, padx=10)
        
        for i, personality in enumerate(personality_types):
            # Put half in first column, half in second
            if i < len(personality_types) // 2:
                parent = col1_frame
                row = i
            else:
                parent = col2_frame
                row = i - len(personality_types) // 2
                
            rb = ttk.Radiobutton(parent, text=personality, value=personality,
                                variable=self._personality_vars['personality_picker'])
            rb.grid(row=row, column=0, sticky="w", pady=2)
        
        # Update the scroll region when the size changes
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Add OK and Cancel buttons
        button_frame = ttk.Frame(picker_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                 command=picker_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        ok_button = ttk.Button(button_frame, text="OK", 
                             command=lambda: self._apply_personality_selection(picker_window))
        ok_button.pack(side=tk.RIGHT, padx=5)
        
    def _apply_personality_selection(self, window):
        """Apply the selected personality type and close the window."""
        selected = self._personality_vars['personality_picker'].get()
        self._personality_vars['personality_type'].set(selected)
        window.destroy()

    def _create_quirks_subtab(self, parent):
        """Populates the Quirks sub-tab with personality trait checkboxes."""
        # Main container for quirks
        quirks_container = ttk.Frame(parent)
        quirks_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a grid of personality trait checkboxes
        # We'll organize them into columns for better layout
        
        # Define all the quirk options
        quirks = [
            "Small Bladder", "Always Hungry", "Oblivious",
            "Slutty", "Bitchy", "Pervert",
            "Loves Reading", "Loves Music", "Active",
            "Passive", "Friendly", "Fastidious",
            "Lazy", "Elusive", "Solitary",
            "Sporty", "Serious", "Into Girls"
        ]
        
        # Create BooleanVars for each quirk
        for quirk in quirks:
            var_name = f"quirk_{quirk.lower().replace(' ', '_')}"
            self._personality_vars[var_name] = tk.BooleanVar(value=False)
        
        # Define the grid layout
        num_columns = 3
        rows_per_column = (len(quirks) + num_columns - 1) // num_columns  # Ceiling division
        
        # Create frames for each column
        for col in range(num_columns):
            col_frame = ttk.Frame(quirks_container)
            col_frame.grid(row=0, column=col, padx=10, sticky="n")
            
            # Add checkboxes to this column
            for i in range(rows_per_column):
                idx = col * rows_per_column + i
                if idx < len(quirks):
                    quirk = quirks[idx]
                    var_name = f"quirk_{quirk.lower().replace(' ', '_')}"
                    
                    cb = ttk.Checkbutton(
                        col_frame, 
                        text=quirk,
                        variable=self._personality_vars[var_name]
                    )
                    cb.grid(row=i, column=0, sticky="w", pady=2)
        
        # Add button controls at the bottom
        button_frame = ttk.Frame(quirks_container)
        button_frame.grid(row=1, column=0, columnspan=num_columns, pady=10)
        
        random_button = ttk.Button(button_frame, text="Random", 
                                  command=self._randomize_quirks)
        random_button.grid(row=0, column=0, padx=5)
        
        select_all_button = ttk.Button(button_frame, text="Select All", 
                                      command=lambda: self._toggle_all_quirks(True))
        select_all_button.grid(row=0, column=1, padx=5)
        
        deselect_all_button = ttk.Button(button_frame, text="Deselect All", 
                                        command=lambda: self._toggle_all_quirks(False))
        deselect_all_button.grid(row=0, column=2, padx=5)
    
    def _randomize_quirks(self):
        """Randomly select quirks."""
        import random
        
        # Get all quirk variables
        quirk_vars = {k: v for k, v in self._personality_vars.items() if k.startswith('quirk_')}
        
        # Reset all to False
        for var in quirk_vars.values():
            var.set(False)
        
        # Random number of quirks to select (between 1 and 1/3 of all quirks)
        num_quirks = len(quirk_vars)
        num_to_select = random.randint(1, max(1, num_quirks // 3))
        
        # Randomly select some quirks
        selected_vars = random.sample(list(quirk_vars.values()), num_to_select)
        for var in selected_vars:
            var.set(True)
    
    def _toggle_all_quirks(self, state):
        """Set all quirks to the given state (True/False)."""
        # Get all quirk variables
        quirk_vars = {k: v for k, v in self._personality_vars.items() if k.startswith('quirk_')}
        
        # Set all to the given state
        for var in quirk_vars.values():
            var.set(state)

    def _create_questions_subtab(self, parent):
        """Populates the Questions sub-tab with Yes/No questions."""
        # Main container for questions
        questions_container = ttk.Frame(parent)
        questions_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # List of questions to ask
        questions = [
            "Fond of animals?",
            "Enjoys eating?",
            "Enjoys cooking?",
            "Plays sports?",
            "Studious?",
            "Fashionable?",
            "Drinks coffee straight?",
            "Eats spicy food?",
            "Has a sweet tooth?",
            "Morning person?",
            "Likes rain?",
            "Enjoys shopping?"
        ]
        
        # Create a frame for each question with Yes/No radiobuttons
        for i, question in enumerate(questions):
            question_frame = ttk.Frame(questions_container)
            question_frame.grid(row=i, column=0, sticky="w", pady=5)
            
            # Question label
            ttk.Label(question_frame, text=question).grid(row=0, column=0, sticky="w", padx=5)
            
            # Create variable for this question
            var_name = f"question_{question.lower().replace('?', '').replace(' ', '_')}"
            self._personality_vars[var_name] = tk.BooleanVar(value=True)  # Default to Yes
            
            # Radiobutton frame
            rb_frame = ttk.Frame(question_frame)
            rb_frame.grid(row=0, column=1, padx=20)
            
            # Yes radiobutton
            yes_rb = ttk.Radiobutton(
                rb_frame, 
                text="Yes",
                value=True,
                variable=self._personality_vars[var_name]
            )
            yes_rb.grid(row=0, column=0, padx=20)
            
            # No radiobutton
            no_rb = ttk.Radiobutton(
                rb_frame, 
                text="No",
                value=False,
                variable=self._personality_vars[var_name]
            )
            no_rb.grid(row=0, column=1, padx=20)
            
        # Button group at the bottom
        button_frame = ttk.Frame(questions_container)
        button_frame.grid(row=len(questions), column=0, pady=10)
        
        # Random button
        random_button = ttk.Button(button_frame, text="Randomize Answers", 
                                 command=self._randomize_questions)
        random_button.pack(side=tk.LEFT, padx=5)
        
        # All Yes button
        all_yes_button = ttk.Button(button_frame, text="All Yes", 
                                  command=lambda: self._set_all_questions(True))
        all_yes_button.pack(side=tk.LEFT, padx=5)
        
        # All No button
        all_no_button = ttk.Button(button_frame, text="All No", 
                                 command=lambda: self._set_all_questions(False))
        all_no_button.pack(side=tk.LEFT, padx=5)
    
    def _randomize_questions(self):
        """Randomly set Yes/No answers to questions."""
        import random
        
        # Get all question variables
        question_vars = {k: v for k, v in self._personality_vars.items() 
                        if k.startswith('question_')}
        
        # Set each to a random True/False value
        for var in question_vars.values():
            var.set(random.choice([True, False]))
    
    def _set_all_questions(self, value):
        """Set all questions to the same answer (True=Yes, False=No)."""
        # Get all question variables
        question_vars = {k: v for k, v in self._personality_vars.items() 
                        if k.startswith('question_')}
        
        # Set all to the given value
        for var in question_vars.values():
            var.set(value)

    def _create_preferences_subtab(self, parent):
        """Populates the Preferences sub-tab with relationship and interaction preferences."""
        # Container for all preference content
        preferences_container = ttk.Frame(parent)
        preferences_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a notebook for sub-categories
        pref_notebook = ttk.Notebook(preferences_container)
        pref_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for each preference category
        relationship_frame = ttk.Frame(pref_notebook)
        interaction_frame = ttk.Frame(pref_notebook)
        content_frame = ttk.Frame(pref_notebook)  # Add a new frame for content settings
        conversation_frame = ttk.Frame(pref_notebook)
        
        # Add frames to the notebook
        pref_notebook.add(relationship_frame, text="Relationship")
        pref_notebook.add(interaction_frame, text="Interaction")
        pref_notebook.add(content_frame, text="Content Level")  # Add the new tab
        pref_notebook.add(conversation_frame, text="Conversation")
        
        # Populate each sub-category
        self._create_relationship_preferences(relationship_frame)
        self._create_interaction_preferences(interaction_frame)
        self._create_content_preferences(content_frame)  # Add method call for the new tab
        self._create_conversation_preferences(conversation_frame)
    
    def _create_relationship_preferences(self, parent):
        """Create relationship preference options."""
        # Container for relationship preferences
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Frame for selecting relationship type
        rel_type_frame = ttk.LabelFrame(container, text="Relationship Type", padding=10)
        rel_type_frame.pack(fill=tk.X, pady=5)
        
        # Relationship type options
        relationship_types = [
            "Friend", "Best Friend", "Mentor", "Student", 
            "Partner", "Spouse", "Crush", "Admirer",
            "Colleague", "Assistant", "Advisor", "Therapist"
        ]
        
        # Variable to store relationship type
        self._personality_vars['relationship_type'] = tk.StringVar(value="Friend")
        
        # Create radio buttons in a grid layout
        cols = 4
        for i, rel_type in enumerate(relationship_types):
            row = i // cols
            col = i % cols
            
            rb = ttk.Radiobutton(
                rel_type_frame,
                text=rel_type,
                value=rel_type,
                variable=self._personality_vars['relationship_type']
            )
            rb.grid(row=row, column=col, sticky="w", padx=10, pady=2)
        
        # Frame for relationship dynamics
        dynamics_frame = ttk.LabelFrame(container, text="Relationship Dynamics", padding=10)
        dynamics_frame.pack(fill=tk.X, pady=10)
        
        # Dynamics questions
        dynamics_questions = [
            "Is playful teasing OK?",
            "Use pet names/terms of endearment?",
            "Show protective tendencies?",
            "Express jealousy sometimes?",
            "Tell personal stories?",
            "Share secrets?"
        ]
        
        # Create a frame for each dynamics question
        for i, question in enumerate(dynamics_questions):
            q_frame = ttk.Frame(dynamics_frame)
            q_frame.grid(row=i, column=0, sticky="w", pady=3)
            
            # Question label
            ttk.Label(q_frame, text=question).grid(row=0, column=0, sticky="w", padx=5)
            
            # Create variable for this question
            var_name = f"rel_dyn_{question.lower().replace('?', '').replace(' ', '_')}"
            self._personality_vars[var_name] = tk.BooleanVar(value=True)  # Default to Yes
            
            # Radiobutton frame
            rb_frame = ttk.Frame(q_frame)
            rb_frame.grid(row=0, column=1, padx=20)
            
            # Yes radiobutton
            ttk.Radiobutton(rb_frame, text="Yes", value=True,
                          variable=self._personality_vars[var_name]).grid(row=0, column=0, padx=20)
            
            # No radiobutton
            ttk.Radiobutton(rb_frame, text="No", value=False,
                          variable=self._personality_vars[var_name]).grid(row=0, column=1, padx=20)
        
    def _create_interaction_preferences(self, parent):
        """Create interaction preference options."""
        # Container for interaction preferences
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Frame for comfort levels
        comfort_frame = ttk.LabelFrame(container, text="Comfort Levels", padding=10)
        comfort_frame.pack(fill=tk.X, pady=5)
        
        # Interaction comfort questions
        comfort_questions = [
            "Is casual physical contact OK?",
            "Is flirting OK?",
            "Is mild romantic content OK?",
            "Is sharing personal details OK?"
        ]
        
        # Create a frame for each comfort question
        for i, question in enumerate(comfort_questions):
            q_frame = ttk.Frame(comfort_frame)
            q_frame.grid(row=i, column=0, sticky="w", pady=3)
            
            # Question label
            ttk.Label(q_frame, text=question).grid(row=0, column=0, sticky="w", padx=5)
            
            # Create variable for this question
            var_name = f"comfort_{question.lower().replace('?', '').replace(' ', '_')}"
            self._personality_vars[var_name] = tk.BooleanVar(value=True)  # Default to Yes
            
            # Radiobutton frame
            rb_frame = ttk.Frame(q_frame)
            rb_frame.grid(row=0, column=1, padx=20)
            
            # Yes radiobutton
            ttk.Radiobutton(rb_frame, text="Yes", value=True,
                          variable=self._personality_vars[var_name]).grid(row=0, column=0, padx=20)
            
            # No radiobutton
            ttk.Radiobutton(rb_frame, text="No", value=False,
                          variable=self._personality_vars[var_name]).grid(row=0, column=1, padx=20)
        
        # Frame for behavior traits
        behavior_frame = ttk.LabelFrame(container, text="Behavior Traits", padding=10)
        behavior_frame.pack(fill=tk.X, pady=10)
        
        # Behavior trait options
        behavior_traits = [
            "Shy", "Confident", "Formal", "Casual",
            "Reserved", "Expressive", "Serious", "Playful"
        ]
        
        # Variables for behavior traits (using scales)
        for i, (left_trait, right_trait) in enumerate(zip(behavior_traits[::2], behavior_traits[1::2])):
            trait_frame = ttk.Frame(behavior_frame)
            trait_frame.pack(fill=tk.X, pady=5)
            
            # Left trait label
            ttk.Label(trait_frame, text=left_trait).pack(side=tk.LEFT, padx=5)
            
            # Create variable for this trait pair
            var_name = f"trait_{left_trait.lower()}_{right_trait.lower()}"
            self._personality_vars[var_name] = tk.IntVar(value=50)  # Default to middle
            
            # Scale for the trait
            scale = ttk.Scale(
                trait_frame,
                from_=0,  # Left trait = 0
                to=100,   # Right trait = 100
                orient=tk.HORIZONTAL,
                variable=self._personality_vars[var_name],
                length=200
            )
            scale.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            # Right trait label
            ttk.Label(trait_frame, text=right_trait).pack(side=tk.LEFT, padx=5)
    
    def _create_content_preferences(self, parent):
        """Create content level preference options."""
        # Container for content preferences
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Content Level Settings
        content_frame = ttk.LabelFrame(container, text="Content Level", padding=10)
        content_frame.pack(fill=tk.X, pady=5)
        
        # Content Level options
        self._personality_vars['content_level'] = tk.StringVar(value="family")
        
        ttk.Label(content_frame, text="Select the content level for interactions:").pack(anchor="w", pady=5)
        
        content_options = [
            ("Family-friendly", "family", "Safe for all ages, no mature or explicit content"),
            ("Mature", "mature", "May include mature themes but no explicit content"),
            ("Adult", "adult", "May include adult themes and explicit content")
        ]
        
        for display_text, value, description in content_options:
            option_frame = ttk.Frame(content_frame)
            option_frame.pack(fill=tk.X, pady=2)
            
            rb = ttk.Radiobutton(
                option_frame,
                text=display_text,
                value=value,
                variable=self._personality_vars['content_level']
            )
            rb.pack(side=tk.LEFT)
            
            ttk.Label(option_frame, text=f" - {description}", foreground="gray").pack(side=tk.LEFT, padx=5)
            
        # Age verification checkbox for adult content
        age_frame = ttk.Frame(content_frame)
        age_frame.pack(fill=tk.X, pady=5)
        
        self._personality_vars['age_verified'] = tk.BooleanVar(value=False)
        age_check = ttk.Checkbutton(
            age_frame,
            text="I confirm I am at least 18 years old (required for adult content)",
            variable=self._personality_vars['age_verified']
        )
        age_check.pack(anchor="w")
        
        # Warning label
        ttk.Label(
            content_frame, 
            text="Note: Adult content requires age verification and may be subject to additional restrictions.",
            foreground="red"
        ).pack(anchor="w", pady=5)
        
        # Relationship Type Settings
        relationship_frame = ttk.LabelFrame(container, text="Relationship Mode", padding=10)
        relationship_frame.pack(fill=tk.X, pady=10)
        
        # Relationship Type options
        self._personality_vars['relationship_type'] = tk.StringVar(value="friend")
        
        ttk.Label(relationship_frame, text="Select relationship mode:").pack(anchor="w", pady=5)
        
        relationship_options = [
            ("Friend", "friend", "Casual and friendly conversations"),
            ("Romantic", "romantic", "Romantic and affectionate interactions"),
            ("Companion", "companion", "Supportive and personal interactions")
        ]
        
        for display_text, value, description in relationship_options:
            option_frame = ttk.Frame(relationship_frame)
            option_frame.pack(fill=tk.X, pady=2)
            
            rb = ttk.Radiobutton(
                option_frame,
                text=display_text,
                value=value,
                variable=self._personality_vars['relationship_type']
            )
            rb.pack(side=tk.LEFT)
            
            ttk.Label(option_frame, text=f" - {description}", foreground="gray").pack(side=tk.LEFT, padx=5)

    def _create_conversation_preferences(self, parent):
        """Create conversation preference options."""
        # Container for conversation preferences
        container = ttk.Frame(parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Frame for communication style
        style_frame = ttk.LabelFrame(container, text="Communication Style", padding=10)
        style_frame.pack(fill=tk.X, pady=5)
        
        # Communication style options
        style_options = [
            "Concise", "Detailed", "Formal", "Casual",
            "Literal", "Metaphorical", "Factual", "Emotional",
            "Direct", "Indirect", "Serious", "Humorous"
        ]
        
        # Create a grid of style option scales (6 rows, 2 columns)
        for i in range(0, len(style_options), 2):
            if i+1 < len(style_options):
                left_style = style_options[i]
                right_style = style_options[i+1]
                
                row = i // 2
                
                # Style pair frame
                pair_frame = ttk.Frame(style_frame)
                pair_frame.grid(row=row, column=0, sticky="ew", pady=5)
                
                # Left style label
                ttk.Label(pair_frame, text=left_style).pack(side=tk.LEFT, padx=5)
                
                # Create variable for this style
                var_name = f"style_{left_style.lower()}"
                self._personality_vars[var_name] = tk.IntVar(value=50)  # Default to middle
                
                # Scale for the style
                scale = ttk.Scale(
                    pair_frame,
                    from_=0,  # Minimum
                    to=100,   # Maximum
                    orient=tk.HORIZONTAL,
                    variable=self._personality_vars[var_name],
                    length=150
                )
                scale.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
                
                # Right style label
                ttk.Label(pair_frame, text=right_style).pack(side=tk.LEFT, padx=5)
        
        # Frame for conversation topics
        topics_frame = ttk.LabelFrame(container, text="Favorite Conversation Topics", padding=10)
        topics_frame.pack(fill=tk.X, pady=10)
        
        # Topics options
        topics = [
            "Arts", "Science", "Technology", "Philosophy",
            "History", "Current Events", "Personal Matters", "Hobbies",
            "Travel", "Food", "Literature", "Entertainment"
        ]
        
        # Create checkboxes for topics in a grid layout
        cols = 3
        for i, topic in enumerate(topics):
            row = i // cols
            col = i % cols
            
            # Variable for this topic
            var_name = f"topic_{topic.lower()}"
            self._personality_vars[var_name] = tk.BooleanVar(value=False)
            
            # Checkbox
            cb = ttk.Checkbutton(
                topics_frame,
                text=topic,
                variable=self._personality_vars[var_name]
            )
            cb.grid(row=row, column=col, sticky="w", padx=10, pady=2)
        
        # Button to randomize preferences
        random_button = ttk.Button(
            container,
            text="Randomize All Preferences",
            command=self._randomize_preferences
        )
        random_button.pack(pady=10)
    
    def _randomize_preferences(self):
        """Randomize all preference settings."""
        import random
        
        # Get boolean variables (checkboxes and radiobuttons)
        bool_vars = {k: v for k, v in self._personality_vars.items() 
                    if isinstance(v, tk.BooleanVar) and 
                    (k.startswith('comfort_') or k.startswith('rel_dyn_') or k.startswith('topic_'))}
        
        # Randomize boolean variables
        for var in bool_vars.values():
            var.set(random.choice([True, False]))
        
        # Get integer variables (scales)
        int_vars = {k: v for k, v in self._personality_vars.items() 
                   if isinstance(v, tk.IntVar) and 
                   (k.startswith('trait_') or k.startswith('style_'))}
        
        # Randomize scales
        for var in int_vars.values():
            var.set(random.randint(0, 100))
        
        # Randomize relationship type
        if 'relationship_type' in self._personality_vars:
            relationship_types = [
                "Friend", "Best Friend", "Mentor", "Student", 
                "Partner", "Spouse", "Crush", "Admirer",
                "Colleague", "Assistant", "Advisor", "Therapist"
            ]
            self._personality_vars['relationship_type'].set(random.choice(relationship_types))

    def _create_description_subtab(self, parent):
        """Populates the Description sub-tab."""
        # Add a Text widget for free-form description
        # Placeholder - we'll implement this next
        self.description_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Default placeholder text
        placeholder = "Enter a detailed description of the AI's character, background, and personality here.\n\nExample:\nChika is a cheerful and energetic young woman who loves to help others. She has a pure heart and always sees the good in people. She loves music and reading, and is quite studious. She enjoys cooking and is especially good at baking sweet treats. She's a bit naive sometimes but her genuine nature makes her endearing to everyone around her."
        
        self.description_text.insert(tk.END, placeholder)
        self._personality_vars['description'] = self.description_text # Store text widget itself for now

    def _apply_personality_settings(self):
        """Saves the current UI settings into the self.personality_settings dict."""
        self.logger.info("Applying personality settings...")
        self.personality_settings.clear() # Start fresh

        for key, tk_var in self._personality_vars.items():
            try:
                if isinstance(tk_var, (tk.StringVar, tk.BooleanVar, tk.IntVar)):
                    self.personality_settings[key] = tk_var.get()
                elif isinstance(tk_var, tk.Text) or isinstance(tk_var, scrolledtext.ScrolledText):
                     self.personality_settings[key] = tk_var.get("1.0", tk.END).strip()
                # Add handling for other widget types (e.g., Combobox) if needed
                else:
                     self.logger.warning(f"Unhandled widget type for key '{key}': {type(tk_var)}")
            except Exception as e:
                self.logger.error(f"Error getting value for key '{key}': {e}")

        # Log the collected settings (for debugging)
        self.logger.info(f"Collected Settings: {self.personality_settings}")

        # Update the main app status
        if hasattr(self.main_app, 'status_var'):
             self.main_app.status_var.set("Personality settings applied.")
        else:
             self.logger.warning("Main app instance does not have 'status_var'.")

        # Send these settings to the LLM interface for the AI to use in responses
        try:
            if hasattr(self.main_app, 'llm'):
                self.main_app.llm.update_personality(self.personality_settings)
                
                # Display feedback about key settings
                feedback_msg = "Personality settings applied to AI"
                
                # Add content level info if available
                if 'content_level' in self.personality_settings:
                    content_level = self.personality_settings['content_level'].capitalize()
                    feedback_msg += f" (Content: {content_level}"
                
                    # Check if adult content is properly verified
                    if content_level == "Adult" and not self.personality_settings.get('age_verified', False):
                        feedback_msg += " - downgraded to Mature due to missing age verification)"
                    else:
                        feedback_msg += ")"
                
                # Add relationship type if available
                if 'relationship_type' in self.personality_settings:
                    relationship = self.personality_settings['relationship_type'].capitalize()
                    if 'content_level' not in self.personality_settings:
                        feedback_msg += f" (Relationship: {relationship})"
                    else:
                        feedback_msg += f" (Relationship: {relationship})"
                
                feedback_msg += "."
                self.main_app.add_message("System", feedback_msg, animate=False)
        except Exception as e:
            self.logger.error(f"Error updating LLM personality: {e}")
            
    def _save_personality(self):
        """Save the current personality settings to a file."""
        # First apply the current settings
        self._apply_personality_settings()
        
        # Then save to a file
        try:
            from ai_core.gui.utils import ask_save_file, save_json_file
            
            filename = ask_save_file(
                title="Save Personality Profile",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                defaultextension=".json"
            )
            
            if filename:
                success = save_json_file(filename, self.personality_settings)
                if success:
                    self.main_app.add_message("System", f"Personality profile saved to {filename}", animate=False)
                else:
                    self.main_app.add_message("System", "Failed to save personality profile", animate=False)
        except Exception as e:
            self.logger.error(f"Error saving personality profile: {e}")
            self.main_app.add_message("System", f"Error saving personality profile: {str(e)}", animate=False)
            
    def _load_personality(self):
        """Load personality settings from a file."""
        try:
            from ai_core.gui.utils import ask_open_file, load_json_file
            
            filename = ask_open_file(
                title="Load Personality Profile",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            if filename:
                loaded_settings = load_json_file(filename)
                if loaded_settings:
                    # Update the UI with loaded settings
                    self._apply_loaded_settings(loaded_settings)
                    self.main_app.add_message("System", f"Personality profile loaded from {filename}", animate=False)
                else:
                    self.main_app.add_message("System", "Failed to load personality profile", animate=False)
        except Exception as e:
            self.logger.error(f"Error loading personality profile: {e}")
            self.main_app.add_message("System", f"Error loading personality profile: {str(e)}", animate=False)
            
    def _apply_loaded_settings(self, settings):
        """Apply loaded settings to the UI widgets."""
        for key, value in settings.items():
            if key in self._personality_vars:
                var = self._personality_vars[key]
                try:
                    if isinstance(var, (tk.StringVar, tk.BooleanVar, tk.IntVar)):
                        var.set(value)
                    elif isinstance(var, tk.Text) or isinstance(var, scrolledtext.ScrolledText):
                        var.delete("1.0", tk.END)
                        var.insert("1.0", value)
                    else:
                        self.logger.warning(f"Unhandled widget type for key '{key}': {type(var)}")
                except Exception as e:
                    self.logger.error(f"Error setting value for key '{key}': {e}")
        
        # Update internal settings
        self.personality_settings = settings.copy()
        
        # Apply to the LLM
        try:
            if hasattr(self.main_app, 'llm'):
                self.main_app.llm.update_personality(self.personality_settings)
        except Exception as e:
            self.logger.error(f"Error updating LLM personality: {e}")