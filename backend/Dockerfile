# Use an official Python runtime as a parent image
FROM python:3.9

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libatk-bridge2.0-0 \
        libdrm2 \
        libatspi2.0-0 \
        libgbm1 \
        libasound2 \
        libnspr4 \
        libnss3 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libxkbcommon0 \
        ffmpeg \
        xvfb \
        xauth \
    && rm -rf /var/lib/apt/lists/*


# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
RUN pip install poetry

COPY pyproject.toml poetry.lock src/download.py ./

#RUN poetry install --no-root
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

RUN playwright install-deps

RUN playwright install chromium

RUN python download.py

COPY . /app

# Expose the port your application listens on (if applicable)
EXPOSE 8000

ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Copy a startup script
COPY bin/entry_point.sh ./
RUN chmod +x /app/entry_point.sh

# Define the command to run your application
ENTRYPOINT ["/app/entry_point.sh"]

CMD ["uvicorn", "src.endpoint:app", "--host", "0.0.0.0", "--reload"]
