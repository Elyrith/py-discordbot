# Build this with: docker build -t discord-discordbot .
# Or use the docker-compose file: docker-compose up -d

FROM python:latest

RUN useradd -u 1000 -m discordbot
USER discordbot
WORKDIR /home/discordbot

COPY --chown=discordbot:discordbot . .
RUN pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

CMD ["python3", "launcher.py"]