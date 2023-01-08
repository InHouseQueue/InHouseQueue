#!/bin/bash

# Set the file name
echo "Enter the name of the tar file:"
read file_name

# Set the directory based on the value of DIRECTORY
if [ "$DIRECTORY" = "staging" ]; then
  DIRECTORY_PATH="/root/s3-bucket-2/staging"
  INHOUSE_DB_VOLUME="inhousequeue_inhouse-db"
  INHOUSE_QUEUE_DIRECTORY="/root/InHouseQueue"
else
  DIRECTORY_PATH="/root/s3-bucket-2/production"
  INHOUSE_DB_VOLUME="inhousequeue-live_inhouse-db"
  INHOUSE_QUEUE_DIRECTORY="/root/InHouseQueue-live"
fi

# Copy the tar file from the specified directory to /root/backups
cp "$DIRECTORY_PATH/$file_name" /root/backups

# Extract the tar file in /root/backups
tar -xvzf /root/backups/$file_name -C /root/backups

# Run "docker-compose down" in the specified InHouseQueue directory
cd "$INHOUSE_QUEUE_DIRECTORY" || exit
docker-compose down

# Remove the inhousequeue_inhouse-db volume
docker volume rm "$INHOUSE_DB_VOLUME"
docker volume rm inhousequeue_inhouse-db

# Run the cp command to copy main.sqlite to the inhousequeue_inhouse-db volume
docker run --rm -it -v INHOUSE_DB_VOLUME:/INHOUSE_DB_VOLUME -v /root/backups/backup/inhouse-db-backup:/archive:ro alpine cp /archive/main.sqlite /INHOUSE_DB_VOLUME

# Remove the "backup" directory and tar file from /root/backups
rm -r /root/backups/backup
rm /root/backups/$file_name