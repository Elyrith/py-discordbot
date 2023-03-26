# Build this with: docker build -t discord-loudfootbot .
FROM python:latest
WORKDIR /root
ENV HOME /root/
COPY *.py $HOME/
ADD cogs $HOME/cogs
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python3", "launcher.py"]