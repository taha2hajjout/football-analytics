FROM python:3.12-slim
# python:3.12-slim = official Python image, "slim" means minimal size

WORKDIR /app
# sets the working directory inside the container — all commands run from here

COPY requirements.txt .
# copy requirements first (before the rest of the code)
# Docker caches this layer — if requirements didn't change, it skips reinstalling

RUN pip install -r requirements.txt
# installs all Python libraries inside the container
# runs once when you build the image, not every time you start it

COPY . .
# copy the rest of your project files into the container

EXPOSE 8501
# tells Docker this container listens on port 8501 (Streamlit's default)

CMD ["python", "-m", "streamlit", "run", "app/app.py", "--server.address=0.0.0.0"]
# the command that runs when the container starts
# --server.address=0.0.0.0 makes Streamlit accessible from outside the container
