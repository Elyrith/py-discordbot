# Build this with: docker build -t discord-discordbot .
# Or use the docker-compose file: docker-compose up -d

FROM python:latest

RUN useradd -u 1000 -m discordbot
USER discordbot
WORKDIR /home/discordbot

ADD ./requirements.txt /tmp/requirements.txt
RUN pip install --user --no-cache-dir --no-warn-script-location -r /tmp/requirements.txt

COPY --chown=discordbot:discordbot . .

CMD ["python3", "launcher.py"]