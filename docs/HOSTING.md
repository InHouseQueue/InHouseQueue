# How to host this on a server - Docker

## Running the bot with Docker - Available on Docker [hub:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue)
### Prerequisites
- Installation of [Docker](https://docs.docker.com/get-docker/)
- Working knowledge of docker

1. Pull the latest image `docker pull henrykoleoso/in-house-queue`
2. Run the bot `docker run -v db:/app/db -e TOKEN=[discord-token] -d henrykoleoso/in-house-queue`
3. Stop the bot `docker stop [containerid]`
4. View the docker repository for specific tags/versions that are [available:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue) you can then pull a specific version/tag `docker pull henrykoleoso/in-house-queue:v1.0.2-beta`
5. Details of what is included in the versions are on the [release](https://github.com/HenrySpartGlobal/InHouseQueue/releases) page.
6. Keep an eye out on the [release](https://github.com/HenrySpartGlobal/InHouseQueue/releases) page for updates!

**IMPORTANT:**
`-v db:/app/db` creates a named volume. It is called `db` (feel free to change this if you like). This volume is attached to the docker container, and it contains the `main.sqlite` which is your DATABASE. It has all the important data about your server, leaderboard, set channels, wins and so on. Keep it safe and don't forget to [attach](https://www.geeksforgeeks.org/mounting-a-volume-inside-docker-container/) it when you pull a new image!

# How to host this on a server - VPS (Ubuntu with SystemD )
I've made it very easy to deploy this bot in a [CI/CD](https://www.redhat.com/en/topics/devops/what-is-ci-cd) fashion. Systemd controls the Bot and will automatically restart the bot if you merge into your main branch.

*Note: When the bot restarts all queues will be reset. Although the bot restarts almost instantly, it's still recommended to restart at low traffic times!*

## Prerequisites

- A server - Recommended Ubuntu - I am using `Ubuntu 22.04 LTS x64`
- A fork of this repo 
- Discord Bot [Token](https://discord.com/developers/applications/)
- IP Address of your server
- SSH Username of your server (default is *usually* `root`)
- SSH Password to get into your server
- Port of your server (default is usually `22`)

I use [Vultr](https://my.vultr.com/deploy/) to deploy the bot, but any other VPS will work fine.

A YouTube video going over this in **a lot** of detail - [here](https://www.youtube.com/watch?v=iI9TyX-a5z0). 

**NOTE: I have since updated the way I do this to be more reliable. The YouTube video will work, but it's not the way I will show you below.**

Feel free to use my Vultr $100 free hosting credit [link](https://www.vultr.com/?ref=9182917-8H), if you decide to use Vultr that is!

## GitHub Actions workflows
1. Once you have forked this repo, delete everything in inside `.github/workflows` **apart from** `deploy-bot-v2.yml` and `update-bot-v2.yml`.
2. Log on to your VPS Server via a terminal or Putty for windows. I do `ssh root@123.123.123` then enter my password when prompted.
3. In a folder of your choice, run `sudo -Hu root ssh-keygen -t rsa`. Press enter a few times. If you have a linux user, then replace `root` with that user.
4. This will create an SSH Key pair. Copy the contents of `.ssh/id_rsa.pub`.
5. On your GitHub Repo go to, Settings > Security > Deploy Keys. Paste the `id_rsa.pub` content in here and give it a nice name.
6. To confirm this is working, you should now be able to clone your repo from your VPS server with `git clone git@github.com:{username}/{reponame}.git`. Delete it with `rm -r {reponame}`. The pipeline will do this for us later.
7. In your repo `Settings` navigate to `secrets` and then `actions`. Create 5 Secrets. Use these **exact** names.
   1. `BOT_TOKEN` - This will be your Discord Bot Token. 
      1. **IMPORTANT** - You must paste it in this format `TOKEN=XXXXXXXXXXXXXXXXX`
   2. `HOST` - Paste in the IP address of your server
   3. `USERNAME` - Paste the Username of your server, usually default as `root`.
   3. `PASSWORD` - Paste in your Password.
   3. `PORT` - Paste in Port, usually default as `22`.
8. Make sure the `default` branch in your Repo is called `main`. This is usually the GitHub default anyway.
9. Navigate to `Actions` in your GitHub Repo. There should now be 2 Workflows. Click on `Deploy New Bot v2`, and run the Workflow on the `main` branch.
10. This will set up the server and create Systemd services. I go into more details on my [YouTube video](https://www.youtube.com/watch?v=iI9TyX-a5z0) explaining my Infrastructure design. 
11. Once this has run successfully, your bot should be online. 
12. Now back in the Actions tab run the `Update Bot v2` work flow manually, or create a commit to the main branch to test this. This will restart the bot. 

Once it's successful, everytime you merge into your `main` branch, the bot will restart and will have the new code on your server - automatically. Be careful not to merge anything into the main branch whilst people are using the Bot!
My YouTube video has more details on how to start, restart, stop and debug the bot once it is running. Time stamp here [25:13](https://www.youtube.com/watch?v=iI9TyX-a5z0&t=1513s)
Any questions about this or the video please visit my [Support Discord](https://discord.gg/NDKMeT6GE7) Page
