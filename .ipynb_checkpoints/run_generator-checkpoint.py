import os
import sys

# Ensure the script can find the managers folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "managers"))

from sample_data_generator import SampleDataGenerator  # import directly from the file

generator = SampleDataGenerator()
generator.generate_all()
