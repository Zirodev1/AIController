"""
Command processor for handling special commands in the chat.
"""
import logging
import re

class CommandProcessor:
    """Process text commands in chat"""
    
    def __init__(self, main_window):
        """Initialize the command processor.
        
        Args:
            main_window: The main application window with access to all components
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.command_prefix = "/"
        
        # Command handlers dictionary
        self.commands = {
            "help": self._cmd_help,
            "mode": self._cmd_mode,
            "voice": self._cmd_voice,
            "vision": self._cmd_vision,
            "clear": self._cmd_clear,
            "save": self._cmd_save,
            "camera": self._cmd_camera,
            "personality": self._cmd_personality,
            "debug": self._cmd_debug,
            "image": self._cmd_image,
            "status": self._cmd_status,
            "memory": self._cmd_memory
        }
        
    def process_text(self, text):
        """Check if text is a command and process accordingly.
        
        Args:
            text: The text input to check and process
            
        Returns:
            bool: True if text was a command and was processed, False otherwise
        """
        if not text.startswith(self.command_prefix):
            return False
            
        # Extract command without prefix
        command_text = text[len(self.command_prefix):].strip()
        return self.handle_command(command_text)
            
    def handle_command(self, command_text):
        """Process command text.
        
        Args:
            command_text: Command text without the prefix
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        # Split into command and arguments
        parts = command_text.split()
        if not parts:
            self._show_help("No command specified")
            return True
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Check if command exists
        if cmd in self.commands:
            try:
                # Call the appropriate command handler
                self.commands[cmd](args)
                return True
            except Exception as e:
                self.logger.error(f"Error processing command '{cmd}': {e}")
                self.main_window.add_message("System", f"Error processing command: {str(e)}", animate=False)
                return True
        else:
            self._show_unknown_command(cmd)
            return True
            
    def _show_help(self, message=None):
        """Show help information.
        
        Args:
            message: Optional message to show before help text
        """
        if message:
            self.main_window.add_message("System", message, animate=False)
            
        # Show available commands
        help_text = "Available commands:\n"
        help_text += "  /help - Show this help message\n"
        help_text += "  /mode [family|mature|adult] - Set content mode\n"
        help_text += "  /voice [on|off] - Toggle voice output\n"
        help_text += "  /vision [on|off] - Toggle vision system\n"
        help_text += "  /clear - Clear chat history\n"
        help_text += "  /save [filename] - Save chat to file\n"
        help_text += "  /camera [list|reset] - Camera controls\n"
        help_text += "  /personality [list|load name] - Personality controls\n"
        help_text += "  /debug [on|off] - Toggle debug mode\n"
        help_text += "  /image <prompt> - Generate an image\n"
        help_text += "  /memory [clear|save|load] - Memory management\n"
        help_text += "  /status - Show system status"
        
        self.main_window.add_message("System", help_text, animate=False)
    
    def _show_unknown_command(self, cmd):
        """Show message for unknown command.
        
        Args:
            cmd: The unknown command
        """
        self.main_window.add_message("System", f"Unknown command: '{cmd}'. Type /help for available commands.", animate=False)
        
    def _cmd_help(self, args):
        """Handle help command.
        
        Args:
            args: Command arguments
        """
        self._show_help()
        
    def _cmd_mode(self, args):
        """Handle mode command for setting content mode.
        
        Args:
            args: Command arguments
        """
        if not args:
            # Show current mode
            current_mode = self.main_window.llm.get_content_mode()
            self.main_window.add_message("System", f"Current content mode: {current_mode}", animate=False)
            self.main_window.add_message("System", "Usage: /mode [family|mature|adult]", animate=False)
            return
            
        # Set mode
        mode = args[0].lower()
        if mode in ["family", "mature", "adult"]:
            # If adult mode, verify age
            if mode == "adult" and not self._verify_adult_mode():
                return
                
            # Set the content mode
            self.main_window.llm.set_content_mode(mode)
            self.main_window.add_message("System", f"Content mode set to: {mode}", animate=False)
        else:
            self.main_window.add_message("System", f"Invalid mode: {mode}. Use 'family', 'mature', or 'adult'.", animate=False)
            
    def _verify_adult_mode(self):
        """Verify that adult mode can be enabled."""
        # Check if age verification is already done in personality settings
        if hasattr(self.main_window, 'personality_tab') and hasattr(self.main_window.personality_tab, '_personality_vars'):
            vars = self.main_window.personality_tab._personality_vars
            if 'age_verified' in vars and vars['age_verified'].get():
                return True
                
        # Otherwise, warn the user
        self.main_window.add_message("System", "Adult mode requires age verification. Please go to Personality > Preferences > Content Level and check the age verification box.", animate=False)
        return False
            
    def _cmd_voice(self, args):
        """Handle voice command for controlling voice output.
        
        Args:
            args: Command arguments
        """
        if not args:
            # Toggle voice
            self.main_window._toggle_output_mode()
            status = "enabled" if self.main_window.use_voice_output else "disabled"
            self.main_window.add_message("System", f"Voice output {status}", animate=False)
            return
            
        # Set voice state
        state = args[0].lower()
        if state in ["on", "enable", "true", "1", "yes"]:
            self.main_window.use_voice_output = True
            self.main_window.add_message("System", "Voice output enabled", animate=False)
        elif state in ["off", "disable", "false", "0", "no"]:
            self.main_window.use_voice_output = False
            self.main_window.add_message("System", "Voice output disabled", animate=False)
        else:
            self.main_window.add_message("System", f"Invalid voice state: {state}. Use 'on' or 'off'.", animate=False)
            
    def _cmd_vision(self, args):
        """Handle vision command for controlling vision system.
        
        Args:
            args: Command arguments
        """
        if not args:
            # Toggle vision
            self.main_window.vision_tab.toggle_vision()
            return
            
        # Set vision state
        state = args[0].lower()
        if state in ["on", "enable", "true", "1", "yes"]:
            if not self.main_window.use_vision:
                self.main_window.vision_tab.toggle_vision()
        elif state in ["off", "disable", "false", "0", "no"]:
            if self.main_window.use_vision:
                self.main_window.vision_tab.toggle_vision()
        else:
            self.main_window.add_message("System", f"Invalid vision state: {state}. Use 'on' or 'off'.", animate=False)
            
    def _cmd_clear(self, args):
        """Handle clear command for clearing chat.
        
        Args:
            args: Command arguments
        """
        self.main_window.chat_tab.clear_chat()
        
    def _cmd_save(self, args):
        """Handle save command for saving chat.
        
        Args:
            args: Command arguments
        """
        filename = args[0] if args else None
        self.main_window.chat_tab.save_chat(filename)
        
    def _cmd_camera(self, args):
        """Handle camera command for camera controls.
        
        Args:
            args: Command arguments
        """
        if not args:
            # Show camera status
            if hasattr(self.main_window, 'vision_system') and self.main_window.vision_system:
                status = self.main_window.vision_system.get_vision_info()
                self.main_window.add_message("System", f"Camera status: {status}", animate=False)
            else:
                self.main_window.add_message("System", "Vision system not initialized", animate=False)
            self.main_window.add_message("System", "Usage: /camera [list|reset]", animate=False)
            return
            
        # Handle camera subcommands
        subcmd = args[0].lower()
        if subcmd == "list":
            self.main_window.vision_tab._list_cameras()
        elif subcmd == "reset" or subcmd == "recover":
            self.main_window.vision_tab._attempt_camera_recovery()
        else:
            self.main_window.add_message("System", f"Invalid camera command: {subcmd}. Use 'list' or 'reset'.", animate=False)
            
    def _cmd_personality(self, args):
        """Handle personality command for personality controls.
        
        Args:
            args: Command arguments
        """
        if not args:
            # Show current personality settings
            if hasattr(self.main_window, 'personality_tab'):
                settings = self.main_window.personality_settings
                name = settings.get('name', 'Default')
                personality_type = settings.get('personality_type', 'None')
                relationship = settings.get('relationship_type', 'Friend')
                
                info = f"Current personality: {name}\n"
                info += f"Type: {personality_type}\n"
                info += f"Relationship: {relationship}"
                
                self.main_window.add_message("System", info, animate=False)
            else:
                self.main_window.add_message("System", "Personality system not initialized", animate=False)
            return
            
        # Handle personality subcommands
        subcmd = args[0].lower()
        if subcmd == "list":
            # This would list available saved personalities
            self.main_window.add_message("System", "Saved personalities not yet implemented", animate=False)
        elif subcmd == "load" and len(args) > 1:
            # This would load a saved personality
            personality_name = args[1]
            self.main_window.add_message("System", f"Loading personality '{personality_name}' not yet implemented", animate=False)
        else:
            self.main_window.add_message("System", "Usage: /personality [list|load name]", animate=False)
            
    def _cmd_debug(self, args):
        """Handle debug command for toggling debug mode.
        
        Args:
            args: Command arguments
        """
        if not args:
            # Toggle debug mode
            if hasattr(self.main_window, 'vision_tab'):
                current = self.main_window.vision_tab.debug_var.get()
                self.main_window.vision_tab.debug_var.set(not current)
                self.main_window.vision_tab._toggle_debug()
                status = "enabled" if not current else "disabled"
                self.main_window.add_message("System", f"Debug mode {status}", animate=False)
            else:
                self.main_window.add_message("System", "Vision system not initialized", animate=False)
            return
            
        # Set debug state
        state = args[0].lower()
        if state in ["on", "enable", "true", "1", "yes"]:
            if hasattr(self.main_window, 'vision_tab'):
                self.main_window.vision_tab.debug_var.set(True)
                self.main_window.vision_tab._toggle_debug()
                self.main_window.add_message("System", "Debug mode enabled", animate=False)
        elif state in ["off", "disable", "false", "0", "no"]:
            if hasattr(self.main_window, 'vision_tab'):
                self.main_window.vision_tab.debug_var.set(False)
                self.main_window.vision_tab._toggle_debug()
                self.main_window.add_message("System", "Debug mode disabled", animate=False)
        else:
            self.main_window.add_message("System", f"Invalid debug state: {state}. Use 'on' or 'off'.", animate=False)
            
    def _cmd_image(self, args):
        """Handle image command for generating images.
        
        Args:
            args: Command arguments
        """
        if not args:
            self.main_window.add_message("System", "Usage: /image <prompt>", animate=False)
            return
            
        # Join all args to form the prompt
        prompt = " ".join(args)
        
        # Create image generation text
        image_request_text = f"generate image {prompt}"
        
        # Process as a normal image generation request
        self.main_window._process_input(image_request_text)
        
    def _cmd_status(self, args):
        """Handle status command for showing system status.
        
        Args:
            args: Command arguments
        """
        # Build status report
        status = "System Status:\n"
        
        # Voice status
        status += f"Voice output: {'enabled' if self.main_window.use_voice_output else 'disabled'}\n"
        status += f"Voice input: {'enabled' if self.main_window.use_voice_input else 'disabled'}\n"
        
        # Vision status
        vision_active = "enabled" if hasattr(self.main_window, 'use_vision') and self.main_window.use_vision else "disabled"
        status += f"Vision system: {vision_active}\n"
        
        if hasattr(self.main_window, 'vision_system') and self.main_window.vision_system:
            vision_info = self.main_window.vision_system.get_info()
            status += f"Camera status: {vision_info.camera_status}\n"
            status += f"Face detection: {'active' if vision_info.face_detected else 'inactive'}\n"
        
        # Content mode
        if hasattr(self.main_window, 'llm'):
            content_mode = self.main_window.llm.get_content_mode() if hasattr(self.main_window.llm, 'get_content_mode') else "unknown"
            status += f"Content mode: {content_mode}\n"
            
        # Personality info
        if hasattr(self.main_window, 'personality_settings') and self.main_window.personality_settings:
            settings = self.main_window.personality_settings
            name = settings.get('name', 'Default')
            status += f"Active personality: {name}"
        
        self.main_window.add_message("System", status, animate=False)
        
    def _cmd_memory(self, args):
        """Handle memory management commands.
        
        Args:
            args: Command arguments
        """
        if not args:
            # Show memory status
            if hasattr(self.main_window, 'memory_manager'):
                context_count = len(self.main_window.memory_manager.get_recent_context(100))
                status = f"Memory status: {context_count} exchanges in memory"
                self.main_window.add_message("System", status, animate=False)
            else:
                self.main_window.add_message("System", "Memory system not initialized", animate=False)
                
            self.main_window.add_message("System", "Usage: /memory [clear|save|load]", animate=False)
            return
            
        # Handle memory subcommands
        subcmd = args[0].lower()
        
        if subcmd == "clear":
            # Clear memory
            if hasattr(self.main_window, 'memory_manager'):
                self.main_window.memory_manager.clear_memory()
            else:
                self.main_window.add_message("System", "Memory system not initialized", animate=False)
                
        elif subcmd == "save":
            # Save memory to file
            if hasattr(self.main_window, 'memory_manager'):
                filename = args[1] if len(args) > 1 else None
                self.main_window.memory_manager.save_conversation(filename)
            else:
                self.main_window.add_message("System", "Memory system not initialized", animate=False)
                
        elif subcmd == "load":
            # Load memory from file
            if hasattr(self.main_window, 'memory_manager'):
                if len(args) > 1:
                    filename = args[1]
                    self.main_window.memory_manager.load_conversation(filename)
                else:
                    # List available saved conversations
                    files = self.main_window.memory_manager.list_saved_conversations()
                    if files:
                        self.main_window.add_message("System", "Available saved conversations:", animate=False)
                        for file in files:
                            self.main_window.add_message("System", f"- {file}", animate=False)
                        self.main_window.add_message("System", "Use /memory load <filename> to load a conversation", animate=False)
                    else:
                        self.main_window.add_message("System", "No saved conversations found", animate=False)
            else:
                self.main_window.add_message("System", "Memory system not initialized", animate=False)
                
        elif subcmd == "list":
            # List available saved conversations
            if hasattr(self.main_window, 'memory_manager'):
                files = self.main_window.memory_manager.list_saved_conversations()
                if files:
                    self.main_window.add_message("System", "Available saved conversations:", animate=False)
                    for file in files:
                        self.main_window.add_message("System", f"- {file}", animate=False)
                else:
                    self.main_window.add_message("System", "No saved conversations found", animate=False)
            else:
                self.main_window.add_message("System", "Memory system not initialized", animate=False)
                
        else:
            self.main_window.add_message("System", f"Unknown memory command: {subcmd}", animate=False)
            self.main_window.add_message("System", "Usage: /memory [clear|save|load|list]", animate=False)