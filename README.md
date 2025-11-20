# magicompose
Automatic docker compose file generator wrtitten in Python

## Usage :
> start a new magicompose project
```bash
magicompose.py # will use the current directory as project (add it to you path to use it from anywhere
```
> use magicompose
```bash
show services | show_services | ss # list the current services created
show networks | show_networks | sn # list the current networks created

add service | add_service | as # create a new service (follow instructions)
add network | add_network | an # create a new network (not fully implemented, only subnets available) (follow instructions

edit service <name> | edit_service <name> | es <name> # edit the choosen service
edit network <name> | edit_network <name> | en <name> # edit the choosen network

clear # clear terminal
export # export the docker-compose.yml file
exit # exit magicompose
```

## Dev :
> upcomming features will be added soon such as auto Dockerfile creation and support
