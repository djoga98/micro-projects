#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

# Configuration
CLI_SCRIPT = "cli.py"
GUI_SCRIPT = "gui.py"

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import pygame
        return True
    except ImportError:
        return False

def print_banner():
    """Display the Matrix-style banner"""
    banner = """
    ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗
    ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝
    ██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝ 
    ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗ 
    ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
    ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
    
    Welcome to The Matrix - Choose your reality
    """
    print(banner)

def show_menu():
    """Display the selection menu"""
    print("\nSelect simulation mode:")
    print("1. CLI Mode - Terminal matrix rain")
    print("2. GUI Mode - Graphical matrix effect")
    print("3. Exit")
    print("-" * 40)

def get_user_choice():
    """Get and validate user input"""
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)
        except EOFError:
            print("\n\nExiting...")
            sys.exit(0)

def run_cli_matrix():
    """Launch the CLI version"""
    try:
        print("Launching CLI Matrix simulation...")
        print("Press Ctrl+C to return to menu\n")
        subprocess.run([sys.executable, str(CLI_SCRIPT)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running CLI version: {e}")
        return False
    except KeyboardInterrupt:
        print("\nReturning to main menu...")
        return True

def run_gui_matrix():
    """Launch the GUI version"""
    if not check_dependencies():
        print("Error: pygame is not installed.")
        print("Install it with: pip install pygame")
        return False
    
    try:
        print("Launching GUI Matrix simulation...")
        print("Press ESC or close window to return to menu\n")
        subprocess.run([sys.executable, str(GUI_SCRIPT)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running GUI version: {e}")
        return False
    except KeyboardInterrupt:
        print("\nReturning to main menu...")
        return True

def main():
    """Main program loop"""
    try:
        while True:
            # clear screen for better UX
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print_banner()
            show_menu()
            
            choice = get_user_choice()
            
            if choice == 1:
                success = run_cli_matrix()
                if not success:
                    input("\nPress Enter to continue...")
            
            elif choice == 2:
                success = run_gui_matrix()
                if not success:
                    input("\nPress Enter to continue...")
            
            elif choice == 3:
                print("\nExiting The Matrix...")
                print("Remember, there is no spoon.")
                sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\nForced exit from The Matrix.")
        sys.exit(0)

if __name__ == "__main__":
    main()