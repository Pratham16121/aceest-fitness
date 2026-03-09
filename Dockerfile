# ACEest Fitness - Docker image
# Uses full Python image for Tkinter GUI support
FROM python:3.11-slim

# Install Tkinter and Xvfb (for headless run in CI if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY "accest_fitness.py" .

# Default: run the app (needs display or xvfb-run)
# For headless CI: xvfb-run python "accest fitness.py" --help or similar
CMD ["python", "accest_fitness.py"]
