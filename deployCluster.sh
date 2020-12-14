docker run --rm --net=host -it \
  -v $(pwd)/config:/marzipan/config \
  -v $(pwd)/templates:/marzipan/templates \
  -v $(pwd)/deployments:/marzipan/deployments \
  nlesc/marzipan:latest
