# How to host this on a server

I've made it very easy to deploy this bot in a semi [CI/CD](https://www.redhat.com/en/topics/devops/what-is-ci-cd) fashion. Systemd controls the Bot and will automatically restart the bot if you merge into your main branch.

*Note: When the bot restarts all queues will be reset. Although the bot restarts almost instantly, it's still recommended to restart at low traffic times!*

## Prerequisites

- A server - Recommended Ubuntu - I am using `Ubuntu 22.04 LTS x64`
- A fork or clone of this repo on your GitHub
- Discord Bot [Token](https://discord.com/developers/applications/)
- SSH [Key Pair](https://docs.oracle.com/en/cloud/cloud-at-customer/occ-get-started/generate-ssh-key-pair.html) 
- IP Address of your server
- Username of your server (default is usually root)
- Port of your server (default is usually 22)

I use [Vultr](https://my.vultr.com/deploy/) to deploy the bot, but any other VPS will work fine.

**Note**: I know this will definitely work if you are using Vultr + Ubuntu. Some steps may differ slightly depending on your server provider, but it should be very similar.

A YouTube video going over this in **a lot** of detail - [here](https://www.youtube.com/watch?v=iI9TyX-a5z0)

Feel free to use my Vultr $100 free hosting credit [link](https://www.vultr.com/?ref=9182917-8H), if you decide to use Vultr that is!
## GitHub Actions workflows

1. Delete `.github/workflows/deploy-new-bot-live.yml` and `.github/workflows/update-bot-live.yml` you won't need them.
2. Create 3 Actions secrets. In your repo `Settings` navigate to `secrets` and then `actions`. We'll need to create 3 secrets in here.
   1. `BOT_TOKEN` - This will be your Discord Bot Token. 
      1. **IMPORTANT** - You must paste it in this format `TOKEN = [token-here]`
   2. `HOST` - Paste in the IP address of your server
   3. `SSH_PRIVATE_KEY` - Paste in your SSH PRIVATE Key.
3. Log into your server via SSH or a control panel.
4. Navigate to `./.ssh/authorized_keys`
5. Add your SSH Public Key to this file.
6. If the `port` of your server is not `22` (it should be) update the `deploy-new-bot.yml` `update-bot.yml` files and replace `port` with your port.
7. If your server `user` is anything other than `root` then do the same.
8. Again, you should only have `.github/workflows/deploy-new-bot.yml` and `.github/workflows/update-bot.yml` files. We don't need to change anything else.
9. If you do make any changes to these files, make sure to commit them into your main branch. Speaking of, make sure the `default` branch in your Repo is called `main`.
10. Navigate to `Actions` in your GitHub Repo. There should be 2 Workflows. Click on `Deploy new Bot`, and run the Workflow on the `main` branch.
11. This will set up the server and create Systemd services. I go into more details on my [YouTube video](https://www.youtube.com/watch?v=iI9TyX-a5z0) explaining my Infrastructure design. 
12. Once this has run successfully, your bot should be online. 
13. Last step - Run the `Update Bot` work flow. This will restart the bot again.
14. Once it's successful, everytime you merge into your `main` branch, the bot will restart and will have the new code on your server - automatically. 
15. Any questions about this or the video please visit my [Support Discord](https://discord.gg/NDKMeT6GE7) Page