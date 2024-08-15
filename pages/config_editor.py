import streamlit as st
import yaml
import os

# Helper functions for loading and saving the config
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def save_config(config, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

# Config file path
config_file_path = 'config.yaml'

# Load the current configuration
config = load_config(config_file_path)

st.title("Configuration Editor")

st.write("Update the configuration settings below:")

# Create inputs for each config item
for key in config.keys():
    if isinstance(config[key], list):
        config[key] = st.text_area(f"{key} (comma-separated):", value=", ".join(config[key]))
        config[key] = [item.strip() for item in config[key].split(",")]
    else:
        config[key] = st.text_input(f"{key}:", value=config[key])

# Save changes button
if st.button("Save Changes"):
    save_config(config, config_file_path)
    st.success("Configuration saved successfully!")

st.write("Current Configuration:", config)