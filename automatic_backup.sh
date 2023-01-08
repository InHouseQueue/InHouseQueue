#!/bin/bash

# Set the file name
echo "Enter the name of the tar file:"
read file_name

# Copy the tar file from /root/s3-bucket-2/staging to /root/backups
cp /root/s3-bucket-2/staging/$file_name /root/backups

# Extract the tar file in /root/backups
tar -xvzf /root/backups/$file_name -C /root/backups

# Run "docker-compose down" in the /root/InHouseQueue directory
cd /root/InHouseQueue
docker-compose down

# Remove the inhousequeue_inhouse-db volume
docker volume rm inhousequeue_inhouse-db

# Run the cp command to copy main.sqlite to the inhousequeue_inhouse-db volume
docker run --rm -it -v inhousequeue_inhouse-db:/inhousequeue_inhouse-db -v /root/backups/backup/inhouse-db-backup:/archive:ro alpine cp /archive/main.sqlite /inhousequeue_inhouse-db

# Remove the "backup" directory and tar file from /root/backups
rm -r /root/backups/backup
rm /root/backups/$file_name