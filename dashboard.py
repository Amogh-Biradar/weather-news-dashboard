#!/usr/bin/env python3
"""
Weather and News Dashboard - Main Entry Point
Multi-file Python architecture for a terminal-based dashboard
"""

import sys
import os

# Add workspace root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.news_service import NewsService
from services.weather_service import WeatherService
from services.summary_service import SummaryService


def main():
    """Entry point: initialize services and run the dashboard loop."""
    print("=" * 50)
    print("  🌦️  Weather and News Dashboard")
    print("=" * 50)

    # Initialize services
    news_service = NewsService()
    weather_service = WeatherService()
    summary_service = SummaryService()

    print("Initializing services...")

    # Run the main dashboard loop
    while True:
        print("\n--- DASHBOARD ---")
        print("Options:")
        print("1. Show News Headlines")
        print("2. Show Weather Update")
        print("3. Generate Daily Summary")
        print("4. Exit")
        print("-" * 30)

        try:
            choice = input("Select an option (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n Exiting dashboard...")
            sys.exit(0)

        if choice == "1":
            news_service.fetch_and_get_news()
        elif choice == "2":
            weather_service.fetch_and_display()
        elif choice == "3":
            summary_service.generate_and_save()
        elif choice == "4":
            print("\nGoodbye! 🖤")
            sys.exit(0)
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
