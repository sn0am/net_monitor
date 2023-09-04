# net_monitor

-build command:

docker build . -t image_name

-run container command:

sudo docker run -d --name net_monitor --restart unless-stopped image_name
