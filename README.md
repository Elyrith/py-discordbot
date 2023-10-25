# DiscordBot - A simple, working Discord bot

[![Python App](https://github.com/Elyrith/py-discordbot/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/Elyrith/py-discordbot/actions/workflows/python-app.yml)
[![Docker Image CI](https://github.com/Elyrith/py-discordbot/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/Elyrith/py-discordbot/actions/workflows/docker-image.yml)

#### You will need either:
1. Python and Pip installed on your computer, or
1. Docker installed on your computer

#### An outline of all steps required for this bot are:
1. Create your own server in Discord
1. Create your Discord application (with a bot), and invite it to your server
1. Run this code to start the bot, either in Python (option 1) or Docker (option 2)
1. Testing your bot

#### Good programming strategies this code uses:
1. It pulls the configuration variables (like Discord bot client ID and token) so they can be kept secret and out of the Git repository
1. It introduces cogs to let you make little modules that can be easily added, removed, and reloaded (when changed) without restarting the entire bot
1. It has a test cog you can use to make your own. Copy it, rename it, and enjoy!
1. It uses [Discord's slash commands](https://discord.com/blog/slash-commands-are-here)

---

## Step 1: Create your own Discord server

 Summary: Your bot will need to live in a server, and you can only add bots to Discord servers that you are an admin on. I recommend having your own private server, especially when testing things.

 Privacy Note: Discord bots can have lots of power in a server, including reading chat messages and history, and even listening to voice channels. Since Discord users can't see the code that the bot is using, they can never be sure that the bot is not tracking them. For this reason, I recommend against adding your Discord bot to any server unless _every single user_ trusts you.

1. In the main Discord window the list of servers you are part of is on the left side. At the bottom of that list there are buttons for "Add a Server" (plus sign icon) and "Explore Public Servers" (compass icon). Click on the "Add a Server" button.

 There are two options you can select in the popup you get, but these only change the starting roles, text channels, and voice channels that Discord will automatically create. As the admin, you can _always_ change _anything_ about your server, so don't worry too much about these options right now. The most basic options are "Create My Own" and "For me and my friends", which creates a very basic server. That is good enough for this bot, but you can select whatever you want.

1. Give the server a name, and (optionally) give it a photo icon.

---

## Step 2: Create your Discord application (with a bot), and invite it to your server
Summary: You will need to create a Discord application, then create a Discord bot within that application. That will give you the API data you'll need.

1. To create your Discord application and bot, go to the following URL: https://discord.com/developers/applications/

1. Click "New Application" to create a new application
 1. Give it a name and accept the agreements

1. Click on Bot in the menu on the left, then click Add Bot, and then click "Yes, do it!"
 1. If you have 2-Factor Authentication enabled, it will ask you to pass a verification check here

1. You'll now see your bot's info, and there will be a "Copy" button for the token. Click on that "Copy" button and store that somewhere safe.
 1. That is your bot's "token", so store that somewhere safe for later

1. Scroll down a little to the "Privileged Gateway Intents" section and enable the "Message Content Intent". Your bot will need that to read messages and respond to messages that are commands for it.

1. The final step is to invite your bot to your server:
 1. Click on OAuth2 again, then click "URL Generator"
 1. Check the option that says "bot" (left side, 5th down), then nothing else
 1. Scroll down and "Copy" the generated URL and paste it into the URL bar in a new tab
 1. Login with your Discord credentials (if you aren't already logged in), then select your new server from the dropdown, and click "Authorize"

---

## Step 3: Run this code to start the bot

1. Clone this repository somewhere with internet access

1. Copy the config.py-example file and name the new file simply "config.py"

1. Update the "discordbot_token" with the value from Step 2 earlier and save the file
 1. You can leave the other values alone for now

### Option 1: Run it in Python

4. Install the package requirements by running `pip install -r requirements.txt`

1. Run the bot by running launcher.py (This is usually done by simply typing `python3 launcher.py` in the terminal/command prompt)

### Option 2: Run this code in Docker

4. Make sure you have Docker and docker-compose installed

1. Run `docker-compose up -d`

 Either way, you should now see your bot as a user in your server. If you chose the "Create My Own" and "For me and my friends" options when creating your server, the bot will show up in the "general" text channel, and should be online.

---

## Step 4: Testing your bot

There are a few commands you can run to test if your bot is working. You can type them into a channel that the bot is in, or you can send the bot a direct message.

1. !uptime

 This should have the bot tell you how long it's been online. This test ensures the uptime cog is working correctly.

1. !load cogs.test

 This should load the "test" cog in the "cogs" folder. This test ensures the admin cog is working correctly.

1. !test

 This should have the bot respond to your message with the "thumbsup" emoji, then reply to you with "Test successfuly", then respond to your message with the "ok_hand" emoji. This test ensures the test cog was loaded correctly and is working.