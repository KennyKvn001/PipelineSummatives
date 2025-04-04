# In backend/Dockerfile
FROM continuumio/miniconda3:latest

WORKDIR /app

# Copy environment.yml for conda environment
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "my_env", "/bin/bash", "-c"]

# Copy the rest of the application
COPY . .

# Set PYTHONPATH for proper module resolution
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Run the application with the conda environment
CMD ["conda", "run", "--no-capture-output", "-n", "my_env", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]