
for var in "$@"
do
	echo "Sending file message: $var"
	aws s3 --profile test1 cp "$var" s3://bucket-imageproc-test1-47lining/images/"$var"
done