# Host the Bot yourself - Docker

## Running the Bot with Docker - Available on Docker [hub:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue)
### Prerequisites
- Installation of [Docker](https://docs.docker.com/get-docker/)
- Working knowledge of docker

1. Pull the latest image `docker pull henrykoleoso/in-house-queue`
2. Run the bot `docker run -v db:/app/db -e TOKEN=[discord-token] -d henrykoleoso/in-house-queue`
3. Stop the bot `docker stop [containerid]`
4. View the docker repository for specific tags/versions that are [available:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue). You can then pull a particular version/tag `docker pull henrykoleoso/in-house-queue:v1.0.2-beta`
5. Details of what is included in the versions are on the [release](https://github.com/HenrySpartGlobal/InHouseQueue/releases) page.
6. Keep an eye out on the [release](https://github.com/HenrySpartGlobal/InHouseQueue/releases) page for updates!

**IMPORTANT:**
`-v db:/app/db` creates a named volume. It is called `db` (feel free to change this if you like). This volume is attached to the docker container and contains the `main.sqlite`, your DATABASE. It has all the crucial data about your server, leaderboard, set channels, wins, etc. Please keep it safe, and don't forget to [attach](https://www.geeksforgeeks.org/mounting-a-volume-inside-docker-container/) it when you pull a new image!

# Host the Bot yourself - VPS (Systemd)
I've made it very easy to deploy this Bot in a [CI/CD](https://www.redhat.com/en/topics/devops/what-is-ci-cd) fashion. Systemd controls the Bot and will automatically restart the Bot if you merge into your main branch. 

Follow along, and your Bot will be up in 20 minutes!

*Note: When the Bot restarts, the Bot will reset all queues. Although the Bot restarts almost instantly, it's still recommended to restart at low traffic times!*

## Prerequisites

- A server - Recommended Ubuntu - I am using `Ubuntu 22.04 LTS x64`
- A fork of this Repo 
- Discord Bot [Token](https://discord.com/developers/applications/)
- IP Address of your server
- SSH Username of your server (default is *usually* `root`)
- SSH Password to get into your server
- Port of your server (default is usually `22`)

I use [Vultr](https://my.vultr.com/deploy/) to deploy the Bot, but any other VPS will work fine.

A YouTube video is going over this in **a lot** of detail - [here](https://www.youtube.com/watch?v=iI9TyX-a5z0). 

**NOTE: I have since updated how I do this to be more reliable. The YouTube video will work, but I will show you differently than the way I will show you below.**

Feel free to use my Vultr $100 free hosting credit [link](https://www.vultr.com/?ref=9182917-8H) if you decide to use Vultr that is!

## GitHub Actions workflows
1. Once you have forked this Repo, delete everything inside `.github/workflows` **apart from** `deploy-bot-v2.yml` and `update-bot-v2.yml`.
2. Log on to your VPS Server via a terminal or Putty for windows. I do `ssh root@123.123.123` and then enter my password when prompted.
3. In a folder of your choice, run `sudo -Hu root ssh-keygen -t rsa`. Press enter a few times. If you have a Linux user, then replace `root` with that user.
4. This will create an SSH Key pair. Copy the contents of `.ssh/id_rsa.pub`.
5. On your GitHub Repo, go to, Settings > Security > Deploy Keys. Paste the `id_rsa.pub` content here and give it a nice name.
6. To confirm this is working, you should now be able to clone your Repo from your VPS server with `git clone git@github.com:{username}/{reponame}.git`. Delete it with `rm -r {reponame}`. The pipeline will do this for us later.
7. In your repo `Settings`, navigate to `secrets` and then `actions`. Create 5 Secrets. Use these **exact** names.
   1. `BOT_TOKEN` - This will be your Discord Bot Token. 
      1. **IMPORTANT** - You must paste it in this format `TOKEN=XXXXXXXXXXXXXXXXX`
   2. `HOST` - Paste in the IP address of your server
   3. `USERNAME` - Paste your server's Username, usually default as `root`.
   3. `PASSWORD` - Paste in your password.
   3. `PORT` - Paste in Port, usually default as `22`.
8. Make sure the `default` branch in your Repo is called `main`. This is usually the GitHub default anyway.
9. Navigate to `Actions` in your GitHub Repo. There should now be 2 Workflows. Click on `Deploy New Bot v2`, and run the workflow on the `main` branch.
10. This will set up the server and create Systemd services. I go into more detail on my [YouTube video](https://www.youtube.com/watch?v=iI9TyX-a5z0) explaining my Infrastructure design. 
11. Once this has run successfully, your Bot should be online. 
12. Back in the Actions tab, manually run the `Update Bot v2` workflow or create a commit to the main branch to test this. This will restart the Bot. 

Once it's successful, the Bot will restart every time you merge into your `main` branch. It will have the new code on your server - automatically. Be careful to keep everything from the main branch whilst people are using the Bot!
My YouTube video details how to start, restart, stop and debug the Bot once it is running. Timestamp here [25:13](https://www.youtube.com/watch?v=iI9TyX-a5z0&t=1513s)
If you have any questions about this or the video, please visit my [Support Discord](https://discord.gg/NDKMeT6GE7) Page
