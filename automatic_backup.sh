#!/bin/bash

# Set the file name
echo "Enter the name of the tar file:"
read file_name

# Read the value of AWS_S3_PATH from the .env file
s3_path=$(grep AWS_S3_PATH .env | cut -d '"' -f 2 | cut -d '=' -f 2)

# Set the correct values for the source and destination directories based on the value of AWS_S3_PATH
if [ "$s3_path" == "staging" ]; then
  src_dir="/home/henry/s3-bucket/staging"
  dst_dir="/home/henry/"
  compose_dir="/home/henry/InHouseQueue"
  volume_name="inhousequeue_inhouse-db"
elif [ "$s3_path" == "production" ]; then
  src_dir="/home/henry/s3-bucket/production"
  dst_dir="/home/henry/"
  compose_dir="/home/henry/InHouseQueue-live"
  volume_name="inhousequeue-live_inhouse-db"
else
  echo "Invalid value for AWS_S3_PATH. Must be either 'staging' or 'production'. Value found: $s3_path"
  exit 1
fi

# Copy the tar file from the source directory to the destination directory
cp $src_dir/$file_name $dst_dir || { echo "Error copying tar file. Exiting script."; exit 1; }

cd $dst_dir || { echo "Error copying tar file. Exiting script."; exit 1; }

# Extract the tar file in the destination directory
tar -xvzf $file_name -C $dst_dir || { echo "Error extracting tar file. Exiting script."; exit 1; }

# Change to the correct compose directory
cd $compose_dir || { echo "Error changing to compose directory. Exiting script."; exit 1; }

# Run "docker-compose down" in the compose directory
docker-compose down || { echo "Error running docker-compose down. Exiting script."; exit 1; }

# Remove the volume
docker volume rm $volume_name || { echo "Error removing volume. Exiting script."; exit 1; }

# Run the cp command to copy main.sqlite to the volume
docker run --rm -it -v $volume_name:/$volume_name -v $dst_dir/backup/inhouse-db-backup:/archive:ro alpine cp /archive/main.sqlite /$volume_name || { echo "Error running cp command. Exiting script."; exit 1; }

## Remove the "backup" directory and tar file from the destination directory
rm -r $dst_dir/backup || { echo "Error running rm command. Exiting script."; exit 1; }
rm $dst_dir/$file_name || { echo "Error running rm command. Exiting script."; exit 1; }
