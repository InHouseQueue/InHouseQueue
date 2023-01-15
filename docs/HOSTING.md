# Host the Bot on a server - Docker

## Available on Docker [hub:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue)
### Prerequisites
- Basic Linux command line knowledge (changing directories, renaming files etc.)
- Assuming your server is on Linux Ubuntu - follow this guide to install [docker](https://docs.docker.com/engine/install/ubuntu/)
- You will also need `docker-compose`. Step 1 of this [guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04) usually helps

### Steps
1. First you need to download the code repository files and upload them to your server. You can `git clone` or manually upload the files with something like [FileZilla](https://filezilla-project.org/).
2. Once the files are there, navigate into the InHouseQueue directory.
4. Inside the root directory, delete the existing `docker-compose.yml` and rename `docker-compose-example.yml` to `docker-compose.yml`.
5. If you look at the file you can see it's pretty simple, but there is one important file we still need.
6. Create a `.env` file in the **root** directory.
7. Use this format `TOKEN=XXXXXXXXXXXXXXX`. Save it.
8.You can now run `docker-compose build` and then `docker-compose up -d`.
