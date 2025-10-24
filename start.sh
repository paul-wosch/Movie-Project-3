# To make a this file executable on macOS use `chmod 755 start.sh`.
# After running this command, you can execute the script by typing
# `./start.sh` in the Terminal.
echo "Activating virtual environment..."
source .venv/bin/activate
echo "Starting Python program..."
python3 src/myapp/main.py
echo "Deactivating virtual environment..."
deactivate
echo "Virtual environment deactivated."